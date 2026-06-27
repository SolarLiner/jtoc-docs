#import "@preview/cmarker:0.1.9": render-with-metadata
#import "/template/style.typ": conf

#let parse_date(s) = toml(bytes("date = " + s)).date

#let (meta, body) = render-with-metadata(
  read(sys.inputs.file),
  metadata-block: "frontmatter-yaml",
  scope: (
    image: (source, ..args) => image(source, ..args),
  )
)

#show : conf.with(
  squadron: meta.squadron,
  document-title: meta.title,
  squadron-logo: meta.squadron-logo,
  revisions: meta.revisions.map(entry => (
      date: parse_date(entry.date),
      changes: entry.changes
    )
  )
)

#show "141st JTOC": smallcaps

#body

