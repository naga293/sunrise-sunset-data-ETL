# tap-sunrise-sunset

This is a [Singer](https://singer.io) tap that produces JSON-formatted data
following the [Singer
spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

This tap:

- Pulls raw data from [TheRainery](https://therainery.com/documentation/astronomy)
- Extracts the following resources:
  - Sunrise start time
  - Sunrise end time
  - Sunset start time
  - Sunset end time
- Outputs the schema for each resource
- Incrementally pulls data based on the input state


