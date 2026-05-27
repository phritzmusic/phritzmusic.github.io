/**
 * releases-manual.js — Hand-curated releases
 *
 * Serves as the baseline discography while the Spotify auto-fetch is configured.
 * Once SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET are added as GitHub Secrets,
 * releases-spotify.js will auto-populate and take precedence.
 * Entries with matching Spotify links are automatically deduplicated by main.js.
 */

window.RELEASES_MANUAL = [

  // ─── phritz ────────────────────────────────────────────────────────────────

  {
    title:        "Pods",
    project:      "phritz",
    artwork:      "https://i.scdn.co/image/ab67616d00001e026a50fcc487a4f443dfab30f1",
    link:         "https://open.spotify.com/album/12u78VgU67JnT1LWMg5x7S",
    year:         2025,
    release_date: "2025-03-05"
  },
  // しりべつの冬景をたずねて: removed — Spotify returns this as
  // "a visit to wintry Shiribetsu" (different album ID), deduplicate by title.
  {
    title:        "what if?",
    project:      "phritz",
    artwork:      "https://i.scdn.co/image/ab67616d00001e02ca8e11c61e20ddacabd4030f",
    link:         "https://open.spotify.com/album/4492K0cLjDvAKo2pQrABrR",
    year:         2024,
    release_date: "2024-01-01"
  },
  // Somewhere Blue: removed — Spotify returns this with a different album ID,
  // causing a duplicate. Spotify version takes precedence.
  {
    title:        "Feathering",
    project:      "phritz",
    artwork:      "https://i.scdn.co/image/ab67616d00001e02cde842b4edb34bd281d80945",
    link:         "https://open.spotify.com/album/4oeKTgNU9RbuDSgKS90Fu6",
    year:         2023,
    release_date: "2023-06-01"
  },
  {
    title:        "look at the sky",
    project:      "phritz",
    artwork:      "https://i.scdn.co/image/ab67616d00001e02684e4406d8e67d3f2bfec3c1",
    link:         "https://open.spotify.com/album/6Cmktdp3Qu7SU9Ovuzpmrb",
    year:         2023,
    release_date: "2023-01-20"
  },
  {
    title:        "Just Say So (phritz Remix)",
    project:      "phritz",
    artwork:      "https://i.scdn.co/image/ab67616d00001e02cc54f49be89bb5d95f1c1c2e",
    link:         "https://open.spotify.com/album/6MggUz3bVJvoKzDCiHrSwE",
    year:         2023,
    release_date: "2023-01-01"
  },
  {
    title:        "Blood in blue (phritz Remix)",
    project:      "phritz",
    artwork:      "https://i.scdn.co/image/ab67616d00001e0229dd0130efcdaaa82b637579",
    link:         "https://open.spotify.com/album/47k3uIKCYTkuucDUubo5ZA",
    year:         2023,
    release_date: "2023-01-01"
  },
  {
    title:        "limeade/close enough",
    project:      "phritz",
    artwork:      "https://i.scdn.co/image/ab67616d00001e0294e96f81125ef2dbe19d8ce8",
    link:         "https://open.spotify.com/album/4Cfje8qvP0RdSeXR0FYn94",
    year:         2022,
    release_date: "2022-02-18"
  },
  {
    title:        "sunameri smoke (phritz Remix)",
    project:      "phritz",
    artwork:      "https://i.scdn.co/image/ab67616d00001e02e48b78094aa1e01a5e8b804a",
    link:         "https://open.spotify.com/album/6dyjdWLqEHiq7p0Mm5LZ87",
    year:         2022,
    release_date: "2022-01-01"
  },
  {
    title:        "しりべつのほとりにて",
    project:      "phritz",
    artwork:      "https://i.scdn.co/image/ab67616d00001e02af7cf1055afbd8df149b7a3f",
    link:         "https://open.spotify.com/album/589Ok2ZRu8Vnl2WJxKo0Ss",
    year:         2022,
    release_date: "2022-09-16"
  },
  // grayscale: removed — Spotify returns this with a different album ID,
  // causing a duplicate. Spotify version takes precedence.
  {
    title:        "Love Ride (feat. Shelhiel)",
    project:      "phritz",
    artwork:      "https://i.scdn.co/image/ab67616d00001e02e93dadc41ac4356eadf28197",
    link:         "https://open.spotify.com/album/2Ru26a7wXOG0EuSci7f7R3",
    year:         2021,
    release_date: "2021-01-01"
  },
  {
    title:        "summit",
    project:      "phritz",
    artwork:      "https://i.scdn.co/image/ab67616d00001e02c9f0304d33903d88009b6a94",
    link:         "https://open.spotify.com/album/1yLpmAyxGX4wILfASetPYA",
    year:         2021,
    release_date: "2021-04-07"
  },
  {
    title:        "change my mind",
    project:      "phritz",
    artwork:      "https://i.scdn.co/image/ab67616d00001e02a3dab78f5da144af64f03701",
    link:         "https://open.spotify.com/album/1fd6EH5tcs3HRq12DAPIrX",
    year:         2020,
    release_date: "2020-12-10"
  },

  // ─── tai hirose ────────────────────────────────────────────────────────────

  {
    title:        "nephorandum",
    project:      "tai hirose",
    artwork:      "https://i.scdn.co/image/ab67616d00001e0237200bdd1a14b563d262fbc4",
    link:         "https://open.spotify.com/album/1IB5KVEMRCULCYahkjzAyN",
    year:         2026,
    release_date: "2026-01-01"
  },
  {
    title:        "lifeframe",
    project:      "tai hirose",
    artwork:      "https://i.scdn.co/image/ab67616d00001e02eecccbc276e3bcbb62eb82b9",
    link:         "https://open.spotify.com/album/4r0FnCmNR2Zkd6VA8HDIYW",
    year:         2024,
    release_date: "2024-02-23"
  },
  {
    title:        "giardino",
    project:      "tai hirose",
    artwork:      "https://i.scdn.co/image/ab67616d00001e029586c3a78520361872edddb2",
    link:         "https://open.spotify.com/album/59xTY1YKdQd8DtgnJe2jSy",
    year:         2024,
    release_date: "2024-02-14"
  },
  {
    title:        "hydration and comfort",
    project:      "tai hirose",
    artwork:      "https://i.scdn.co/image/ab67616d00001e02428011a318b84bcb75020b1e",
    link:         "https://open.spotify.com/album/420nf3oonRxkbtAUmJGoRz",
    year:         2024,
    release_date: "2024-02-16"
  },
  {
    title:        "midwinter",
    project:      "tai hirose",
    artwork:      "https://i.scdn.co/image/ab67616d00001e029b83776cf4c78a0071ade541",
    link:         "https://open.spotify.com/album/5uHibu5CEZVhNzVCDuAvgy",
    year:         2024,
    release_date: "2024-03-08"
  },
  {
    title:        "rooms",
    project:      "tai hirose",
    artwork:      "https://i.scdn.co/image/ab67616d00001e02e46717f53ec4584aa9b30108",
    link:         "https://open.spotify.com/album/7waQW7gcDRR6w7s7SbsLWG",
    year:         2024,
    release_date: "2024-03-15"
  },
  {
    title:        "field day",
    project:      "tai hirose",
    artwork:      "https://i.scdn.co/image/ab67616d00001e0289840eb92f3f815b27fa7c37",
    link:         "https://open.spotify.com/album/4uToFUlLaDH4Z4yRSAVRvX",
    year:         2024,
    release_date: "2024-03-01"
  },
  {
    title:        "deepwater / gauze",
    project:      "tai hirose",
    artwork:      "https://i.scdn.co/image/ab67616d00001e023f9c28d374a4e7b0428bd920",
    link:         "https://open.spotify.com/album/6EQLKk52nxcWPq137W173u",
    year:         2023,
    release_date: "2023-09-01"
  },

  // ─── tiny pool centennial ──────────────────────────────────────────────────

  {
    title:        "Brushes",
    project:      "tiny pool centennial",
    artwork:      "https://i.scdn.co/image/ab67616d00001e02ef918e4d0859702423b386fe",
    link:         "https://open.spotify.com/album/5R1DbfwcSj5EO8i7B6bWOG",
    year:         2025,
    release_date: "2025-01-01"
  },

];
