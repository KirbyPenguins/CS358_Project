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
type Expr = Add | Sub | Mul | Div | Lit | Let  


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
    def __str__(self):
        return f"Mul({self.left}, {self.right})"


@dataclass
class Div():
    left : Expr
    right : Expr
    def __str__(self):
        return f"Div({self.left}, {self.right})"


@dataclass
class Lit():
    value : int
    def __str__(self):
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
    match env:
        case ((n,v), *rest) :
            if n == name:
                return v
            else:
                return lookupEnv(name, rest) # type:ignore
        case _ :
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
        # handles the addition
        case Add(left, right):
            match (evalInEnv(env, left), evalInEnv(env, right)):
                case (Lit(l), Lit(r)):
                    return Lit(l + r)
                case _:
                    raise evalError("Addition requires two integer literals")

        # handles the subtraction
        case Sub(left, right):
            match (evalInEnv(env, left), evalInEnv(env, right)):
                case (Lit(l), Lit(r)):
                    return Lit(l - r)
                case _:
                    raise evalError("Subtraction requires two integer literals")

        #Handles the division
        case Mul(left, right):
            match (evalInEnv(env, left), evalInEnv(env, right)):
                case (Lit(l), Lit(r)):
                    return Lit(l * r)
                case _:
                    raise evalError("Multiplication requires two integer literals")

        # handles the division
        case Div(left, right):
            match (evalInEnv(env, left), evalInEnv(env, right)):
                case (Lit(l), Lit(r)):
                    return Lit(l / r)
                case _:
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
            return evalInEnv(extendEnv(env, name, v), body)

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
test_expr = Let(
    name = "combined_image",  # Name of the variable
    value = combine(image1_path, image2_path),  # Expression to combine the images
    body = Name("combined_image")  # Access the resulting combined image
)

# Run the expression
run(test_expr)

# Here is the link to the Pillow https://pillow.readthedocs.io/en/stable/handbook/tutorial.html
'''
The purpose of this project is to create a simple image manipulation language. While 
using the Pillow library. We will create AST node definitions and then create a run 
method
'''