<img width="520" height="402" alt="bkNotidial-Autonovel" src="https://github.com/user-attachments/assets/577bb485-65b7-4977-9ddb-07fb76820ea1" />

# Notidial-Autonovel

**An open-source autonomous pipeline for writing, revising, typesetting, illustrating, and narrating complete novels.**

From a single seed concept → full manuscript, print-ready PDF, ePub, illustrated pages, and narrated audiobook — driven by AI agents.

> Rebuilt from the ground up as a fully open-source alternative inspired by the original [Autonovel](https://github.com/NousResearch/autonovel) project.

---

## Why Notidial-Autonovel?

I started this as a simple refactor of the original Autonovel idea. Two months later it had become a complete ground-up rebuild. The result is a clean, modular, community-first pipeline that anyone can run, extend, and improve.

Originally built as a marketing stunt to generate the origin story of **Mz Domino** — an old-world OSINT investigator with the flair and tenacity of a 1920s gumshoe — it quickly became clear the tool itself was more valuable than any single novel it could produce.

**Mz Domino AI** focuses on robust, privacy-respecting OSINT software orchestrations. Notidial-Autonovel is our gift back to the open-source community.

---

## What It Does

Notidial-Autonovel runs a multi-phase autonomous pipeline:

1. **Foundation** – World, characters, outline, voice, and canon from a seed concept
2. **First Draft** – Sequential chapter writing with evaluation loops
3. **Revision** – Adversarial editing, reader-panel feedback, and iterative rewriting
4. **Production** – Typesetting (PDF/ePub), illustration generation, and narration

The system treats the novel as co-evolving layers (voice, world, characters, outline, prose + canon) and uses modify → evaluate → keep/discard loops to drive quality.

---

## Quick Start

```bash
# Clone the repo
git clone https://github.com/yourusername/Notidial-Autonovel.git
cd Notidial-Autonovel

# Set up environment
cp .env.example .env
# Add your API keys (Anthropic, image gen, TTS, etc.)

# Install dependencies
uv sync   # or pip install -e .

# Generate a seed (or write your own in seed.txt)
python seed.py

# Run the full pipeline
python run_pipeline.py --from-scratch

You can also run individual phases:
Bash
python run_pipeline.py --phase foundation
python run_pipeline.py --phase drafting
python run_pipeline.py --phase revision
python run_pipeline.py --phase production

Pipeline Overview
Phase,What Happens,Exit Condition
Foundation,"World bible, characters, outline, voice, canon",Quality scores above threshold
Drafting,Sequential chapter writing + evaluation,Chapter scores acceptable
Revision,Adversarial edits + multi-persona reader panel,Scores stabilize / improve
Production,"Typesetting, illustrations, narration, packaging",Print-ready & audio 

Key Features

Fully autonomous end-to-end novel generation
Multi-layer co-evolving story architecture
Anti-slop and anti-pattern detection
Adversarial revision loops
Automated typesetting (PDF / ePub)
AI-generated illustrations
Full audiobook narration
Modular design — easy to swap models, prompts, or stages
Open source and built for the community


Example Output
The first novel produced with this pipeline was the origin story of Mz Domino — an OSINT investigator operating with 1920s-era grit in a modern information landscape.
(You can replace this section with links to your actual generated novel, sample chapters, or the PDF/ePub/audio files.)

Project Status
This is a complete, working rebuild. Expect ongoing improvements in:

Prompt quality and evaluation metrics
Cost optimization
Support for more model providers
Better illustration and narration consistency
Documentation and examples

Contributions, issues, and novel-generation stories are very welcome.

Inspiration & Credits
Heavily inspired by the excellent work in NousResearch/autonovel (and the broader Hermes Agent ecosystem). Notidial-Autonovel is an independent ground-up reimplementation focused on openness, modularity, and community ownership.
Also draws conceptual inspiration from systems like karpathy/autoresearch — applying the same autonomous improve-evaluate loop to long-form fiction.

License
MIT

About Mz Domino AI
Mz Domino AI builds privacy-focused OSINT software orchestrations. Our mascot, Mz Domino, is an old-world investigator who never stops digging. This project started as her origin story and grew into something we wanted the whole community to use.

From blank page to finished novel — autonomously.
Star the repo, open an issue, or better yet: generate a novel and tell us what you made.


### Quick customization tips
- Replace `Notidial-Autonovel` and the GitHub URLs with your actual name/repo.
- Add real badges (stars, license, Python version, etc.) at the top.
- Drop in screenshots or a pipeline diagram once you have them.
- Link to your actual generated Mz Domino novel when it’s ready — that’s excellent social proof.
- Expand the “Example Output” and “Contributing” sections as the project matures.

Want a shorter/more minimal version, a more technical deep-dive README, or one that leans harder into the Mz Domino / 1920s gumshoe branding? Just say the word and I’ll revise it.
