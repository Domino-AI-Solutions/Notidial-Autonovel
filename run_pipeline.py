import argparse
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Automatic-Writing-Localy CLI")
    parser.add_argument("--phase", choices=["seed", "foundation", "draft", "revise", "evaluate", "art", "audiobook", "export", "full"], required=True)
    parser.add_argument("--chapter", type=int, default=None)
    
    args = parser.parse_args()

    if args.phase == "seed":
        from scripts.generate_seed import generate_seeds
        generate_seeds()

    elif args.phase == "foundation":
        from scripts.build_foundation import main as build_foundation
        build_foundation()

    elif args.phase == "draft":
        from scripts.draft_and_revise_chapter import draft_and_revise
        if args.chapter:
            draft_and_revise(args.chapter)
        else:
            for i in range(1, 20):
                draft_and_revise(i)

    elif args.phase == "revise":
        from scripts.revise_all_weak_chapters import revise_weak_chapters
        revise_weak_chapters()

    elif args.phase == "evaluate":
        from scripts.anti_slop import main as run_audit
        run_audit()

    elif args.phase == "art":
        from scripts.gen_cover_art import main as run_art
        run_art()

    elif args.phase == "audiobook":
        from scripts.gen_audiobook import main as run_audio
        run_audio()

    elif args.phase == "export":
        from scripts.export import main as run_export
        run_export()

    elif args.phase == "full":
        print("Starting comprehensive pipeline compilation flow...")
        from scripts.build_foundation import main as build_foundation
        from scripts.draft_and_revise_chapter import draft_and_revise
        from scripts.revise_all_weak_chapters import revise_weak_chapters
        from scripts.anti_slop import main as run_audit
        
        build_foundation()
        for i in range(1, 20): # Starting target run
            draft_and_revise(i)
        revise_weak_chapters()
        run_audit()

if __name__ == "__main__":
    main()
import argparse
import sys
import traceback
from pathlib import Path
from run_logger import RunLogger

def main():
    logger = RunLogger.get()
    parser = argparse.ArgumentParser(description="Automatic-Writing-Localy CLI")
    parser.add_argument("--phase", choices=["seed", "foundation", "draft", "revise", "evaluate", "art", "audiobook", "export", "full"], required=True)
    parser.add_argument("--chapter", type=int, default=None)
    
    args = parser.parse_args()

    logger.start_run(args.phase)

    try:
        if args.phase == "seed":
            logger.log(f"Starting seed generation phase")
            from scripts.generate_seed import generate_seeds
            generate_seeds()
            logger.log("Seed generation phase completed")

        elif args.phase == "foundation":
            logger.log(f"Starting foundation build phase")
            from scripts.build_foundation import main as build_foundation
            build_foundation()
            logger.log("Foundation build phase completed")

        elif args.phase == "draft":
            logger.log(f"Starting draft phase (chapter {args.chapter or 'all'})")
            from scripts.draft_and_revise_chapter import draft_and_revise
            if args.chapter:
                draft_and_revise(args.chapter)
            else:
                for i in range(1, 20):
                    draft_and_revise(i)
            logger.log("Draft phase completed")

        elif args.phase == "revise":
            logger.log(f"Starting revision phase")
            from scripts.revise_all_weak_chapters import revise_weak_chapters
            revise_weak_chapters()
            logger.log("Revision phase completed")

        elif args.phase == "evaluate":
            logger.log(f"Starting audit/evaluation phase")
            from scripts.anti_slop import main as run_audit
            run_audit()
            logger.log("Audit/evaluation phase completed")

        elif args.phase == "art":
            logger.log(f"Starting art generation phase")
            from scripts.gen_cover_art import main as run_art
            run_art()
            logger.log("Art generation phase completed")

        elif args.phase == "audiobook":
            logger.log(f"Starting audiobook generation phase")
            from scripts.gen_audiobook import main as run_audio
            run_audio()
            logger.log("Audiobook generation phase completed")

        elif args.phase == "export":
            logger.log(f"Starting manuscript export phase")
            from scripts.export import main as run_export
            run_export()
            logger.log("Manuscript export phase completed")

        elif args.phase == "full":
            logger.log("Starting comprehensive pipeline compilation flow...")
            from scripts.build_foundation import main as build_foundation
            from scripts.draft_and_revise_chapter import draft_and_revise
            from scripts.revise_all_weak_chapters import revise_weak_chapters
            from scripts.anti_slop import main as run_audit
            
            build_foundation()
            for i in range(1, 20): # Starting target run
                draft_and_revise(i)
            revise_weak_chapters()
            run_audit()
            logger.log("Full pipeline completed")

    except Exception as e:
        logger.log(f"[CRASH] Pipeline crashed: {e}")
        logger.log(traceback.format_exc())
        raise
    finally:
        logger.end_run("completed")