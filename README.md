<div id="top"></div>
<!--
*** Thanks for checking out craps. If you have a suggestion that would 
*** make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<h3 align="center">craps</h3>

<br />

<div align="center">
  <!-- <a align="center" href="https://github.com/mhegarty/craps/blob/master/logo.png">
    <img src="https://raw.githubusercontent.com/mhegarty/craps/master/logo.png"
    alt="Logo" width=80 height=80>
  </a> -->
  <a align="center" href="https://github.com/mhegarty/craps/blob/master/logo.png">
    <img src="https://raw.githubusercontent.com/mhegarty/craps/master/logo.png"
    alt="Logo">
  </a>
<br />
<br />
  <p align="center">
    A lightweight table game simulator.
    <!-- <br />
    <a href="https://github.com/mhegarty/craps"><strong>Explore the code »</strong></a>-->
    <br />
    <br />
    ·
    <a href="https://github.com/mhegarty/craps/issues">Report Bug</a>
    ·
    <a href="https://github.com/mhegarty/craps/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<!-- 
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>
-->



<!-- ABOUT THE PROJECT -->
<!--
## About The Project

[![Product Name Screen Shot][product-screenshot]](https://example.com)

Here's a blank template to get started: To avoid retyping too much info. Do a search and replace with your text editor for the following: `mhegarty`, `craps`, `@mjhegarty`, `hegarty`, `email`, `email_client`, `project_title`, `project_description`

<p align="right">(<a href="#top">back to top</a>)</p>
-->

<!--
### Built With

* [Python](https://python.org/)

<p align="right">(<a href="#top">back to top</a>)</p>
-->


<!-- GETTING STARTED -->
<!-- ## Getting Started

The game engine is ready to roll. Let's get rolling.
 -->


<!-- ## Prerequisites

This package uses libraries that have been standard since python 2.7 and it will likely 
run on any python version you are using. If you experience any issues, please [report a bug](https://github.com/mhegarty/craps/issues). -->




## Installation

Install with pip (recommended)
 ```sh
 pip install craps
 ```

<!-- <p align="right">(<a href="#top">back to top</a>)</p> -->



<!-- USAGE EXAMPLES -->
## Usage


```python
!pip install craps
from craps import Game, PassBet, LineOddsBet, ComeBet, PointOddsBet
```

    Collecting craps
      Downloading craps-1.1.0-py3-none-any.whl (9.9 kB)
    Installing collected packages: craps
    Successfully installed craps-1.1.0



```python
# Start a game with $100 at a table with a $10 minimum
g = Game(arrival_cash = 100, minimum_bet=10)

# Place a bet for $10, then roll the dice!
g.bet(PassBet(10))
g.roll()
```

    [Bet] You made a PassBet on the box for 10
    [Rail] You have 990.0 on the rail
    [Table] The shooter is ready, the point is off
    [Table] PassBet for 10 is working on the box
    [Roll] Shooter rolled 10
    [Roll] The point is 10
    [Rail] You have 990.0 on the rail



```python
# Put $20 odds on line bet
g.bet(LineOddsBet(20, g.puck))

# And place an additional come bet for the table minimum
g.bet(ComeBet(g.minimum_bet))
```

    [Bet] You made a LineOddsBet on 10 for 20
    [Rail] You have 970.0 on the rail
    [Bet] You made a ComeBet on the box for 10.0
    [Rail] You have 960.0 on the rail



```python
# Roll!
g.roll()
```

    [Table] The shooter is ready, the point is 10
    [Table] PassBet for 10 is working on 10
    [Table] LineOddsBet for 20 is working on 10
    [Table] ComeBet for 10.0 is working on the box
    [Roll] Shooter rolled 8
    [Roll] 2+6=8 came easy
    [Bet] ComeBet for 10.0 was moved to the 8
    [Rail] You have 960.0 on the rail



```python
# Check your bets
g.callout()
```

    [Table] PassBet for 10 is working on 10
    [Table] LineOddsBet for 20 is working on 10
    [Table] ComeBet for 10.0 is working on 8



```python
# Put $30 odds on your 8
g.bet(PointOddsBet(30, 8))
```

    [Bet] You made a PointOddsBet on 8 for 30
    [Rail] You have 930.0 on the rail



```python
# Roll!
g.roll()
```

    [Table] The shooter is ready, the point is 10
    [Table] PassBet for 10 is working on 10
    [Table] LineOddsBet for 20 is working on 10
    [Table] ComeBet for 10.0 is working on 8
    [Table] PointOddsBet for 30 is working on 8
    [Roll] Shooter rolled 10
    [Roll] Winner!!, 10
    [Payout] PassBet on 10 paid out 20
    [Payout] LineOddsBet on 10 paid out 60.0
    [Rail] You have 1010.0 on the rail


  <!-- <a href="https://github.com/mhegarty/craps/blob/master/images/example.png">
    <img src="https://raw.githubusercontent.com/mhegarty/craps/master/images/example.png"
     alt="Notebook">
  </a> -->

<!-- _For more examples, please refer to the [Documentation](https://example.com)_-->

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- Add Bet types to model.py
  - Add [place bets](https://www.liveabout.com/craps-place-bets-537453)
  - Add [side bets](https://wizardofodds.com/games/craps/appendix/5/)
    - Add the [Yo](https://www.lolcraps.com/craps/bets/yo/) first. That's fun.
- Strategy constructor / builder
  - Logic layer to facilitate strategy construction in a low code environment. For example:
    - `IF` the game puck is off `AND` I do not have a place bet, `THEN` make a place bet.
    - `IF` the game puck is on `AND` I do <u>not</u> have odds on a place or come bet, `THEN` put f(x) odds on it.

See the [open issues](https://github.com/mhegarty/craps/issues) for a full list of proposed features (and known issues).

<!-- <p align="right">(<a href="#top">back to top</a>)</p> -->



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<!-- <p align="right">(<a href="#top">back to top</a>)</p> -->



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<!-- <p align="right">(<a href="#top">back to top</a>)</p> -->



<!-- CONTACT -->
## Contact

Mike Hegarty - [@mjhegarty](https://twitter.com/@mjhegarty) - mike@petorca.com

Project Link: [https://github.com/mhegarty/craps](https://github.com/mhegarty/craps)

<!-- <p align="right">(<a href="#top">back to top</a>)</p> -->



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* Thanks to [@dhegarty19](https://www.instagram.com/dhegarty19/) for agreeing to celebrate our third aniversary at the casino. 
* Big thanks to Othneil Drew for the awesome work on [the best readme template](https://github.com/othneildrew/Best-README-Template)
* [pikpng.com](https://www.pikpng.com/pngvi/hbRwTJb_png-clipart/) for the logo image.


<!-- <p align="right">(<a href="#top">back to top</a>)</p> -->



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/mhegarty/craps.svg?style=for-the-badge
[contributors-url]: https://github.com/mhegarty/craps/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/mhegarty/craps.svg?style=for-the-badge
[forks-url]: https://github.com/mhegarty/craps/network/members
[stars-shield]: https://img.shields.io/github/stars/mhegarty/craps.svg?style=for-the-badge
[stars-url]: https://github.com/mhegarty/craps/stargazers
[issues-shield]: https://img.shields.io/github/issues/mhegarty/craps.svg?style=for-the-badge
[issues-url]: https://github.com/mhegarty/craps/issues
[license-shield]: https://img.shields.io/github/license/mhegarty/craps.svg?style=for-the-badge
[license-url]: https://github.com/mhegarty/craps/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/hegarty
<!-- [product-screenshot]: images/screenshot.png -->