\version "2.20.0"

\header {
  title = "Daar wordt aan de deur geklopt"
  arranger = "M. van der Laaken"
}


global = {
  \key c \major
  \numericTimeSignature
  \time 3/4
}

right = \relative c' {
  g'4. a8 g[ f] e4 c c
  d r r e c c

  g'4. a8 g[ f] e4 c c
  d r r c2.

  d4 r r e c c
  d4 r r e c c
  
  g'4. a8 g[ f] e4 c c
  d r r c2.
}

left = \relative c' {
  \global
  << c,2. e g >> << c, e g >>
  r4 g g r2.

  << c,2. e g >> << c, e g >>
  r4 g g << c,2. e g >>

  r4 g g << e2. g >>
  r4 g g << e2. g >>

  << c,2.~ e g >> << c, e g >>
  r4 g g << c,2. e g >>
}

\score {
  \new PianoStaff \with {
    instrumentName = "Piano"
  } <<
    \new Staff = "right" \with {
      midiInstrument = "acoustic grand"
    } \right
    \new Staff = "left" \with {
      midiInstrument = "acoustic grand"
    } { \clef bass \left }
  >>
  \layout { }
  \midi {
    \tempo 4=100
  }
}
