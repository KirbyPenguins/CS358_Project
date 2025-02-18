from dataclasses import dataclass
from PIL import Image, ImageEnhance

#new value with info 
type Color = image_color | dom_color
type Literal = Name | Image.Image
type Expr = Add | Sub | Mul | Div | Lit | Let  | Neg | And | Or | Not | Eq | Lt | If | Letfun | App | Ifnz


@dataclass
class dom_color():
    image : Image.Image
    def __str__(self):
        return f"Dominant_Color({self.image})"

@dataclass
class image_color():
    image : Image.Image
    def __str__(self) -> str:
        return f"Color({self.image})"


type Action = rotate | Combine
#newly created operators
type new_Action  = lighten | Darken

@dataclass
class Darken():
    image : Image.Image
    def __str__(self):
        return f"Darken({self.image})"

@dataclass
class lighten():
    image : Image.Image
    def __str__(self):
        return f"lighten{self.image}"


@dataclass
class rotate():
    image : Image.Image
    def __str__(self):
        return f"rotate({self.image})"


@dataclass
class Combine():
    image1 : Image.Image
    image2 : Image.Image

    def __str__(self):
        return f"combine({self.image1}, {self.image2})"


@dataclass
class If():
    condition : Expr
    then_branch : Expr
    else_branch : Expr
    def __str__(self):
        return f"If({self.condition}, {self.then_branch}, {self.else_branch})"


@dataclass
class Lt():
    left : Expr
    right : Expr
    def __str__(self):
        return f"lt({self.left}, {self.right})"


@dataclass
class Eq():
    left : Expr
    right : Expr
    def __str__(self):
        return f"Eq({self.left}, {self.right})"


@dataclass
class Not():
    value : Expr
    def __str__(self) -> str:
        return f"Not({self.value})"


@dataclass
class Or():
    left : Expr
    right : Expr
    def __str__(self) -> str:
        return f"or({self.left}, {self.right})"


@dataclass
class And():
    left : Expr
    right : Expr
    def __str__(self):
        return f"and({self.left}, {self.right})"

@dataclass
class Neg():
    value : Expr
    def __str__(self):
        return f"Neg({self.value})"


@dataclass
class Add():
    left : Expr
    right : Expr
    def __str__(self):
        return f"Add({self.left}, {self.right})"


@dataclass
class Sub():
    left : Expr
    right : Expr
    def __str__(self):
        return f"Sub({self.left}, {self.right})"


@dataclass
class Mul():
    left : Expr
    right : Expr
    def __str__(self) -> str:
        return f"Mul({self.left}, {self.right})"


@dataclass
class Div():
    left : Expr
    right : Expr
    def __str__(self):
        return f"Div({self.left}, {self.right})"


@dataclass
class Lit():
    value : int | bool | Image.Image
    def __str__(self) -> str:
        return f"Literal({self.value})"


@dataclass
class Let():
    name : str
    value : Expr
    body : Expr
    def __str__(self):
        return f"(let {self.name} = {self.value} in {self.body})"


@dataclass
class Letfun():
    name: str
    params: list[str]
    bodyexpr: Expr
    inexpr: Expr
    def __str__(self) -> str:
        return f"letfun {self.name} ({",".join(self.params)}) = {self.bodyexpr} in {self.inexpr} end"
    
@dataclass
class App():
    fun: Expr
    args: list[Expr]
    def __str__(self) -> str:
        return f"({self.fun} ({",".join(map(str,self.args))}))"

@dataclass
class Ifnz():
    cond: Expr
    thenexpr: Expr
    elseexpr: Expr
    def __str__(self) -> str:
        return f"(if {self.cond} != 0 then {self.thenexpr} else {self.elseexpr})"
    
@dataclass
class Name():
    name : str
    def __str__(self):
        return self.name


type Binding[V] = tuple[str, V]
type Env[V] = list[Binding[V], ...] # type:ignore this is a type with a arbitary length 

from typing import Any

empty_env : Env[Any] = ()

def extendEnv[V](env : Env[V], name : str, value : V) -> Env[V]:
    return env + ((name, value),)


def lookupEnv[V](name: str, env: Env[V]) -> (V | None) :
    '''Return the first value bound to name in the input environment env
    (or raise an exception if there is no such binding)'''
    # exercises2b.py shows a different implementation alternative
    for n, v in reversed(env):  # Start from the most recent binding
        if n == name:
            return v
    return None


class evalError(Exception):
    pass

class Path:
    p: tuple[Action, ...]


type Value = Image.Image | Path | Closure

@dataclass
class Closure:
    params: list[str]
    body: Expr
    env: Env[Value]

def eval(e: Expr) -> Value:
    return evalInEnv(empty_env, e)

def evalInEnv(env: Env[Value], e: Expr) -> Value:
    match e:
        case dom_color(image):
            image = eval(env, image)  # Evaluate the image expression
            if isinstance(image, Image.Image):
                dominant = image.getcolors(maxcolors=1000000)  # Get colors
                if dominant:
                    dominant_color = max(dominant, key=lambda x: x[0])[1]
                    return dominant_color  # Return the dominant color as an (R, G, B) tuple
                else:
                    raise evalError("No colors found in image")
            else:
                raise evalError("You must provide an image")

        case image_color(image):
            image = eval(env,img)
            if isinstance(image, Image.Image): 
                       # Convert image to RGB if it's not in that mode
                image = image.convert('RGB')
                # Get the pixel data
                pixels = np.array(image)
                # Calculate the average color
                avg_color = pixels.mean(axis=(0, 1))  # Mean along the height and width axes
                # Return the average color as a tuple (R, G, B)
                return tuple(map(int, avg_color)) 
            else:
                raise evalError("You must have images")
                 
        #handles the negate
        case Neg(value):
            v = evalInEnv(env, value)
            if type(v) == int:
                return -v
            else:
                raise evalError("Negation requires an integer literal")

        # handles the addition
        case Add(left, right):
            left_val = evalInEnv(env, left)
            right_val = evalInEnv(env, right)
            if type(left_val) == int and type(right_val) == int:
                return left_val + right_val
            if type(left_val) == Image.Image and type(right_val) == Image.Image:
                new_image = Combine(left_val, right_val)
                return new_image
            else:
                raise evalError("Addition requires two integers literals")

        # handles the subtraction
        case Sub(left, right):
            left_val = evalInEnv(env, left)
            right_val = evalInEnv(env, right)
            if type(left_val) == int and type(right_val) == int:
                return left_val - right_val
            else:
                raise evalError("Subtraction requires two integer literals")

        #Handles the multiplication
        case Mul(left, right):
            left_val = evalInEnv(env, left)
            right_val = evalInEnv(env, right)
            if type(left_val) == int and type(right_val) == int:
                return left_val * right_val
            else:
                raise evalError("Multiplication requires two integer literals")

        # handles the division
        case Div(left, right):
            left_val = evalInEnv(env, left)
            right_val = evalInEnv(env, right)
            if type(left_val) == int and type(right_val) == int:
                if right_val == 0:
                    raise evalError("You cannot divide by Zero")
                return left_val // right_val
            else: 
                raise evalError("Division requires two integer literals")

        # handles the rotate image
        case rotate(image) :
            img = evalInEnv(env,image)
            if isinstance(img, Image.Image):
                return img.rotate(90)
            else:
                return evalError("You can only rotate Photos")

        # handles the combine image
        case Combine(image1, image2) :
            img1 = evalInEnv(env,image1)
            img2 = evalInEnv(env, image2)
            if isinstance(img1, Image.Image) and isinstance(img2, Image.Image):
                if img1.size[1] != img2.size[1]:
                    raise evalError("Images must have the same height")
                w = img1.size[0] + img2.size[0]
                h = max(img1.size[1], img2.size[1])
                combined_image = Image.new("RGB", (w, h))
                combined_image.paste(img1, (0, 0))
                combined_image.paste(img2, (img1.size[0], 0))
                return combined_image
            else:
                raise evalError("Both operands must be images")

        #handles the literals(file path)
        case Name (name) :
            v = lookupEnv(name, env)
            if v is None:
                raise evalError(f"Name {name} not found")
            return v
        
        case Let(name, value, body) :
            v = evalInEnv(env, value)
            new_env = extendEnv(env, name, v)
            return evalInEnv (new_env, body)

        case Lit(lit):
            match lit:
                case int(i):
                    return i
                case bool(b):
                    return b
                case Image.Image():
                    return lit
                case _:
                    raise evalError(f"Unknown literal: {lit}")

        case Or(left, right):
            left_val = evalInEnv(env, left)
            if isinstance(left_val, bool):
                if left_val:
                    return True
                right_val = evalInEnv(env, right)
                if isinstance(right_val, bool):
                    return left_val or right_val
                else:
                    raise evalError("Or requires two boolean literals")
            else:
                raise evalError("Or requires two boolean literals")

        case And(left, right):
            left_val = evalInEnv(env, left)
            if isinstance(left_val, bool):
                if not left_val:
                    return False
                right_val = evalInEnv(env, right)
                if isinstance(right_val, bool):
                    return left_val and right_val
                else:
                    raise evalError("And requires two boolean literals")
            else:
                raise evalError("And requires two boolean literals")


        case Not(value):
            val = evalInEnv(env, value)
            if isinstance(val, bool):
                return not val
            else:
                raise evalError("Not requires a boolean literal")

        case Eq(left, right) :
            left_val = evalInEnv(env, left)
            right_val = evalInEnv(env, right)
            if type (left_val) == bool:
                if type (right_val) == bool:
                    if left_val == True and right_val == True:
                        return True
                    elif left_val == False and right_val == False:
                        return True
                    else:
                        return False
                else:
                    raise evalError("Eq requires a Boolean")
            elif type(left_val) == int and type(right_val) == int:
                if left_val == right_val:
                    return True
                else:
                    return False
            elif isinstance(left_val, Image.Image) and isinstance(right_val, Image.Image):
                return left_val.tobytes() == right_val.tobytes()
            else:
                raise evalError("Eq requires two values of the same type")

        case Lt(left, right) :
            left_val = evalInEnv(env, left)
            right_val = evalInEnv(env, right)
            if type(left_val) == int and type(right_val) == int:
                if left_val < right_val:
                    return True
                else:
                    return False
            else:
                raise evalError("Lt requires a Boolean")

        case If(condition, then_branch, else_branch):
            c = evalInEnv(env, condition)
            if isinstance(c, bool):
                if c:
                    return evalInEnv(env, then_branch)
                else:
                    return evalInEnv(env, else_branch)
            else:
                raise evalError("If condition must be a boolean")

        case Darken(image):
            img = evalInEnv(env, image)
            if isinstance(img, Image.Image):
                enhancer = ImageEnhance.Brightness(img)
                return enhancer.enhance(0.5)
            else:
                raise evalError("Darken requires an image")

        case lighten(image):
            img = evalInEnv(env, image)
            if isinstance(img, Image.Image):
                enhancer = ImageEnhance.Brightness(img)
                return enhancer.enhance(1.5)
            else:
                raise evalError("Lighten requires an image")

        case Ifnz(c,t,e):
            match evalInEnv(env,c):
                case 0:
                    return evalInEnv(env, e)
                case _:
                    return evalInEnv(env,t)
                    
        case Letfun(n,ps,b,i):
            if len(ps) != len(set(ps)):
                raise evalError("duplicate parameter names")
            c = Closure(ps,b,env)
            newEnv = extendEnv(n,c,env)
            c.env = newEnv                # support recursion
            return evalInEnv(newEnv,i) 

        case App(f,es):
            fun = evalInEnv(env,f)
            args = [evalInEnv(env,a) for a in es]
            match fun:
                case Closure(ps,b,cenv):
                    if len(ps) != len(args):
                        raise evalError("wrong number of arguments")
                    newEnv = cenv
                    for (param,arg) in zip(ps,args):
                        newEnv = extendEnv(param,arg,newEnv)
                    return evalInEnv(newEnv,b)

        case _:
            raise evalError(f"Unknown expression: {e}")


def run(e: Expr) -> None:
    # Example of how to use the DSL
    print(f"Running {e}")
    try:
         # Evaluate the expression
        result = eval(e)
        if isinstance(result, Image.Image):
            result.show()
            result.save("answer.png")
        else:
            print(f"Result: {result}") 
        # Optionally, open the result with the default viewer

    except evalError as e:
        print(f"Evaluation error: {e}")

# Test condition
image2_path = Image.open("Image/image2.jpg")
image1_path = Image.open("Image/image1.jpg")

# Define the expression with a proper binding
# Test Expression #1
test1: Expr = Let(
    "image1",  # Name of the variable
    Lit(image1_path),  # Binding the actual image to "image1"
    rotate(Darken(Name("image1")))  # Using the expression properly
)


# Test Expression #2
# Define the expression with the correct transformations
test2: Expr = Let(
    "image1",  # Name of the first variable
    Lit(image1_path),  # Bind image1_path to "image1"
    Let(  # Another Let to bind "image2"
        "image2",  # Name of the second variable
        Lit(image2_path),  # Bind image2_path to "image2"
        Combine(
            lighten(Name("image1")),  # Apply lightening transformation on image1
            Darken(Name("image2"))    # Apply Darkening transformation on image2
        )
    )
)

# Define the expression with a proper binding
# Test Expression #3
test3: Expr = Let(
    "image1",  # Name of the variable
    Lit(image1_path),  # Binding the actual image to "image1"
    rotate(rotate(Name("image1")))  # Using the expression properly
)

# Test Expression #4
# should print error
# Define the expression with the correct transformations
test4: Expr = Let(
    "image1",  # Name of the first variable
    Lit(image1_path),  # Bind image1_path to "image1"
    Let(  # Another Let to bind "image2"
        "image2",  # Name of the second variable
        Lit(3),  # Bind image2_path to "image2"
        Combine(
            lighten(Name("image1")),  # Apply lightening transformation on image1
            (Name("image2"))    # Apply Darkening transformation on image2
        )
    )
)
# Uncomment out the code below to Run the expressions
#run(test1)
#run(test2)
#run(test3)
#run(test4)

# Here is the link to the Pillow https://pillow.readthedocs.io/en/stable/handbook/tutorial.html
'''
The purpose of this project is to create a simple image manipulation language. While 
using the Pillow library. We will create AST node definitions and then create a run 
method. The run method will take an expression and evaluate it. The expression will
be a combination of literals, addition, subtraction, multiplication, division, and
Negate, Equals, less than. This functions implement them and ensures that they are 
integers or booleans for the respective. 

For image manipulation I have created the two operators as  rotate,
and combine. Whenever they are combined or rotate a new photo is made and is saved in a
answer.png where it is easy to view. There will also be a pop up so that you can also 
view it through that. (Please not that it takes a little while for the images to combine).

Another error that has occured is that Whenever I run combine with rotate and a normal image
the photo will combine even though they are not the same dimensions. The reason for this is 
because the rotate adds a border with the same height as the previous image therefore making it
possible. However If you were to combine two images of different heights without rotating it will
not work and an error will pop up.

'''