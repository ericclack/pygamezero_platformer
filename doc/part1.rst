.. _part1:

Part 1
======

Grab the Pac-Man code
---------------------

Our first step is to get the code from the final version of Pac-Man
and check that it works before we do anything else. You can copy and rename your Pac-Man `.py` and `level-1.txt` files, or you can get a fresh copy from GitHub:

Right-click these links to download: 
 * the code: https://github.com/ericclack/pygamezero_platformer/raw/master/platformer0.py
 * a level: https://github.com/ericclack/pygamezero_platformer/raw/master/level-1.txt

Test this out and check everything works.

Let's add some gravity!
-----------------------

Find the :code:`update` function (it's around line 190) and add this
line right at the start of the function:

.. code:: python

   pacman.dy += 0.1

With this one simple change we now have a platformer! Well sort of...
This code will cause our character to fall if there is no block
underneath him or her. Go and try it. You might see some problems:

 1. Your world is designed for Pac-Man not a platformer, so it doesn't work very well and there are too many ghosts!
 2. Our character falls very fast for long drops
 3. Sometimes our character can't get through small gaps.

So you can fix the first point above by editing the file in a text editor. Go and look at `Part 1 of the Pac-Man Tutorial`_ to find out how the file works. 

Here's how we can fix the second point: change the code so that the speed never exceeds `SPEED`:

.. code:: python

   pacman.dy = min(SPEED, pacman.dy + 0.1)

What about the third point? That's a bit more tricky...

What's up with our movement?
----------------------------

TBC


Next up...
----------

In part two of this tutorial we'll get the ghosts moving. Move on to
:ref:`part2`.

.. _Part 1 of the Pac-Man Tutorial: https://pygamezero-pacman.readthedocs.io/en/latest/part1.html
