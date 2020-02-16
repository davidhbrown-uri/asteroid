<!-- ![](asteroid-clipart.jpg) -->
<img src="asteroid-clipart.jpg" height="42" width="42">

# Asteroid the Programming Language

Asteroid is a multi-paradigm programming language heavily influenced by [Python](https://www.python.org), [Lua](http://www.lua.org), [ML](https://www.smlnj.org), and [Prolog](http://www.swi-prolog.org) currently under development at the University of Rhode Island.  Asteroid implements a new programming paradigm called *pattern-matching oriented programming*.  In this new programming paradigm patterns and pattern matching is supported by all major programming language constructs making programs succinct and robust.  Furthermore, patterns themselves are first-class citizens and as such can be passed and returned from functions as well as manipulated computationally.

OK, before we get started here is the obligatory *Hello World!* program written in Asteroid,
```
load "io".

print "Hello World!".
```
Since pattern matching is at the core of Asteroid we find that
the simplest pattern matching occurs in Asteroid's `let` statement. For example,
```
let [x,2,y] = [1,2,3].
```
here the list `[1,2,3]` is matched against the pattern `[x,2,y]` successfully with the corresponding assignments `x` &map; 1 and `y` &map; 3.

Pattern matching can also occur in iteration. Consider,
```
load "io".

let list = [1,2,3].

repeat do
    let [head|list] = list. -- head-tail operator
    print head.
until list is [_].
```
Here we use the head-tail operator as a pattern to match a list. The loop iterates until the list resulting from the repeated application of the head-tail operator has exactly one element in it.  The output of this program is,
```
1
2
```
The following program randomizes a list of names and then creates teams of three
from the randomized list.
```
load "standard".
load "util".
load "io".

-- team participants
let names = [
    "Sofia",
    "Andrew",
    "Evan",
    "Patrick",
    "Julio",
    "Zachary",
    "Joshua",
    "Emily",
    "Samantha",
    "Timothy",
    "Shannon"
  ]

-- shuffle names
let names = shuffle(names).

-- select teams of three
let teams = [].
repeat do
  if length(names) < 3 do
    -- append the remaining names as a team to teams
    let teams = teams + [names].
    let names = []. -- no more names to process
  else do
    -- pattern match the first three names
    let [m1 | m2 | m3 | names] = names.
    let teams = teams + [[m1,m2,m3]].
  end if
until names is [].

-- print teams
for (i,team) in zip(1 to length(teams),teams) do
  let team_str = "".
  repeat do
    let [name|team] = team.
    let team_str = team_str + name + ("" if team is [] else ", ").
  until team is [].
  print("team " + i + (":  " if i < 10 else ": ") + team_str)
end for
```
Here is one instance of output from the program,
```
team 1:  Evan, Timothy, Andrew
team 2:  Patrick, Joshua, Julio
team 3:  Zachary, Emily, Shannon
team 4:  Sofia, Samantha
```
Pattern matching can also happen on function arguments using the `with` or `orwith` keywords.
Here is the canonical factorial program written in Asteroid,

```
-- Factorial

load "standard".
load "io".

function fact
    with 0 do
        return 1
    orwith n do
        return n * fact (n-1).
    end function

print ("The factorial of 3 is: " + fact (3)).
```
As one would expect, the output is,
```
The factorial of 3 is: 6
```

The following quicksort implementation has slightly more complicated patterns for the function
arguments. Asteroid inherits this functionality from functional programming languages such as ML.  
```
-- Quicksort

load "standard".
load "io".

function qsort
    with [] do
        return [].
    orwith [a] do
        return [a].
    orwith [pivot|rest] do
        let less=[].
        let more=[].
        for e in rest do  
            if e < pivot do
                let less = less + [e].
            else do
                let more = more + [e].
            end if
        end for

        return qsort less + [pivot] + qsort more.
    end function

print (qsort [3,2,1,0])
```
The last line of the program prints out the sorted list returned by the quicksort.  The output is,
```
[0,1,2,3]
```
The fact that Asteroid supports matching in all of its major programming constructs and that it has a very flexible view of the interpretations of experssion terms allows the developer to embed symbolic computation right into their programs. The following is a program that uses the [Peano axioms for addition](https://en.wikipedia.org/wiki/Peano_axioms#Addition) to compute addition symbolically.

```
-- implements Peano addition

-- declare the successor function S as a term constructor  
constructor S with arity 1.

-- the 'reduce' function is our reduction engine which recursively pattern matches and
-- rewrites the input term
function reduce
    with a + 0 do                      -- pattern match 'a + 0'
        return reduce a.
    orwith a + S(b)  do                -- pattern match to 'a + S(b)'
        return S(reduce(a + b)).
    orwith term do                     -- default clause
        return term.
    end function

-- construct a term we want to reduce  
let n = S(S(0)) + (S(S(S(0)))).

-- and reduce it!
let rn = reduce n.

-- attach inc interpretation to the S constructor
-- load standard interpretation for `+`
load "standard".
load "util".
load "io".

function inc
    with n do
        return n + 1.
    end function

attach inc to S.

-- show that with this behavior both the original term and the rewritten term
-- evaluate to the same value
print ((eval rn) == (eval n)).
```
The output of this program is,
```
true
```
meaning that the reduced term and the original term with `S` interpreted as the increment function and `+` interpreted in the standard way give the same result,
namely the value `5`.

As mentioned above, Asteroid has a very flexible view of the interpretation of expression terms which allows the programmer to attach new interpretations to constructor symbols on the fly.  Consider the following program which attaches a new interpretation to the `+` operator symbol, performs a computation, and then removes that interpretation restoring the original interpretation,
```
load "standard".  -- load the standard operator interpretations
load "io".        -- load the io system

function funny_add    -- define a function that given two
    with (a, b) do      -- parameters a,b will multiply them
        return a * b.
    end function

attach funny_add to __plus__.   -- attach 'funny_add' to '+'
print (3 + 2).                  -- this will print out the value 6
detach from __plus__.           -- restore default interpretation
print (3 + 2).                  -- this will print out the value 5

-- NOTE: '__plus__' is a special symbol representing the '+' operator
```
The output of the first `print` statement is 6 because `funny_add` attached to the `+` symbol multiplies its arguments.  The second `print` statement outputs the expected value 5 since we are back at the standard interpretation of the `+` symbol.

Asteroid also supports prototype-based OO style programming.  Here is the [dog example](docs.python.org/3/tutorial/classes.html) from the Python documentation cast into Asteroid.  This example builds a list of dog objects that all know some tricks.  We then loop over the list and find all the dogs that know "roll over" using pattern matching.

```
load "standard".
load "io".
load "util".

class Dog with

  data name = "".
  data tricks = [].

  function add_trick
    with (self, new_trick) do
      let self@tricks = self@tricks + [new_trick].
    end function

  function __init__
    with (self, name) do
      let self@name = name.
    end function

  end class

-- Fido the dog
let fido = Dog("Fido").
fido@add_trick("roll over").
fido@add_trick("play dead").

-- Buddy the dog
let buddy = Dog("Buddy").
buddy@add_trick("roll over").
buddy@add_trick("sit stay").

-- Fifi the dog
let fifi = Dog("Fifi").
fifi@add_trick("sit stay").

-- print out all the names of dogs
-- whose first trick is 'roll over'.
let dogs = [fido, buddy, fifi].

for Dog(name, ["roll over"|_], _, _) in dogs do
  print (name + " does roll over").
end for
```
The output of this program is,
```
Fido does roll over
Buddy does roll over
```
Take a look at the [Asteroid User Guide](https://nbviewer.jupyter.org/github/lutzhamel/asteroid/blob/master/Asteroid%20User%20Guide.ipynb) notebook for a more detailed discussion of the language.
