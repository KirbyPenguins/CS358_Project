from dataclasses import dataclass
from PIL import Image


type Action = rotate | combine

@dataclass
class rotate():
    image : Image.Image
    def __str__(self):
        return f"rotate({self.image})"


@dataclass
class combine():
    image1 : Image.Image
    image2 : Image.Image

    def __str__(self):
        return f"combine({self.image1}, {self.image2})"

type Literal = Name | Image.Image
type Expr = Add | Sub | Mul | Div | Lit | Let  | Neg | And | Or | Not | Eq | Lt | If


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
    value : int | bool
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


type Value = Image.Image | Path

def eval(e: Expr) -> Value:
    return evalInEnv(empty_env, e)

def evalInEnv(env: Env[Value], e: Expr) -> Value:
    match e:
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
            img = Image.open(image)
            return img.rotate(90)

        # handles the combine image
        case combine(image1, image2) :
            img1 = Image.open(image1)
            img2 = Image.open(image2)
            if img1.size[1] != img2.size[1]:
                raise EvalError("Images must have the same height")
            w = img1.size[0] + img2.size[0]
            h = max(img1.size[1], img2.size[1])
            combined_image = Image.new("RGB", (w, h))
            combined_image.paste(img1, (0, 0))
            combined_image.paste(img2, (img1.size[0], 0))
            return combined_image

        #handles the literals(file path)
        case Name (name) :
            v = lookupEnv(name, env)
            if v is None:
                raise EvalError(f"Name {name} not found")
            return v
        
        case Let(name, value, body) :
            v = evalInEnv(env, value)
            new_env = extendEnv(env, name, v)
            return evalInEnv (new_env, body)

        case Lit(lit):
            match lit:
                case int(i):
                    return i
                case combine() | rotate():
                    return Path((lit,))
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


        case Not(value) :
            val = evalInEnv(env, value)
            if val == True:
                return False
            elif val == False:
                return True
            elif type(val) == int:
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
            else:
                raise evalError("Eq requires a Boolean")


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
image1_path = "Image/image1.jpg"
image2_path = "Image/image2.jpg"

    
# Define the expression
# Define the expression to combine the images

# Define the expression to combine two images twice

# Run the expression
test1 : Expr = And(Lit(False), Lit(6))
run(test1)

# Here is the link to the Pillow https://pillow.readthedocs.io/en/stable/handbook/tutorial.html
'''
The purpose of this project is to create a simple image manipulation language. While 
using the Pillow library. We will create AST node definitions and then create a run 
method. The run method will take an expression and evaluate it. The expression will
be a combination of literals, addition, subtraction, multiplication, division, and
'''