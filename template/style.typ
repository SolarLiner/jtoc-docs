#import "@preview/hydra:0.6.3": hydra

#let font-title = "Oswald"
#let font-body = "Gelasio"
#let group-name = "141st JTOC"

#let pagetitle(squadron, document-title, squadron-logo) = {
  show text: set text(font: font-title)
  show block: set align(horizon)

  context {
    let frame = if target() == "html" {
      html.frame
    } else {
      x => x
    }

    frame({
      block[#text(size: 32pt, weight: 100, fill: gray, smallcaps(group-name))]
      block[#text(size: 42pt, weight: 100)[#squadron]]
      block[#text(size: 24pt, weight: 100, fill: luma(50%))[#document-title]]
      show image: it => {
        set align(center)
        set block(above: 3cm)
        it
      }
      image(squadron-logo, alt: "logo of the " + squadron + " squadron")
    })
  }
  pagebreak()
}

#let conf(
  squadron: "",
  document-title: "",
  squadron-logo: "",
  revisions: ((date: datetime.today(), changes: ""),),
  doc
) = {
  set document(title: group-name + "—" + squadron + " - " + document-title)
  set page(
    paper: "a4",
    number-align: center,
    margin: 3.5cm,
    numbering: "1",
  )

  set heading(numbering: "1.1.1.")
  show heading: it => if target() != "html" {
    move(
      dx: -measure(counter(heading).display() + " ").width,
      block[#counter(heading).display()~#it.body]
    )
  }
  show heading.where(depth: 1): set text(size: 18pt, weight: 100)
  show heading.where(depth: 2): set text(size: 14pt, weight: 800)
  show figure: set block(breakable: true)
  show heading.where(depth: 1): it => { pagebreak(weak: true); it }

  show ref: set text(fill: blue.darken(50%))
  show link: it => text(fill: blue.darken(20%))[#emoji.chain #it]

  set text(font: font-body)
  set par(justify: true, leading: 1em)

  set page(
    header: columns(2, gutter: 1cm)[
      #set text(font: font-title, size: 9pt, weight: 100)
      #block[
        #block(below: 0.6em)[#text(weight: 300, group-name)]
        #block[#squadron]
      ]
      #colbreak()
      #set align(right)
      #block(text(font: font-body, context hydra(1)))
    ]
  )

  let toplevel = {
    pagetitle(squadron, document-title, squadron-logo)
    
    align(
      center + horizon,
    )[
      #let version = counter("version")
      #table(
        columns: (1fr, 2fr, 5fr), align: (left, left, left,),
        table.header([Version], [Date], [Changes]),
        ..revisions.map(entry => (
          {
            context version.step()
            context version.display("v1")
          },
          entry.date.display("[year]-[month]-[day]"),
          entry.changes
        )).flatten()
      )
      #block(height: 5cm)
      #block(align(left, par(justify: true)[
        This document is reserved for usage within the 141st JTOC and for recreational purposes only, and the procedures described in this document are only intended to work within DCS World and as part of official 141st JTOC missions. It is not adequate for real world flying.
      ]))
    ]

    pagebreak()

    {
      show heading: it => it.body
      outline(title: [Contents])
    }

    pagebreak(to: "odd")

    doc
  }
  
  context if target() == "html" {
    show footnote: {}
    html.html[
      // #html.link(rel: "stylesheet", href: "/assets/css/page.css") // TODO: Find a way to include CSS
      #html.body(toplevel)
    ]
  } else {
    toplevel
  }
}
