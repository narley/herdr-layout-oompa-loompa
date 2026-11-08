import sys, glob, os
from PIL import Image, ImageSequence
B = sys.argv[1]; out = sys.argv[2]
jobs = ["stirrer","taster","taffy","bubble","rower","ticket","cracker","singer"]
sheet = Image.new("RGBA", (8*160, 3*200 + 3*200 + 100), (40,24,16,255))
for i, j in enumerate(jobs):
    for k, st in enumerate(["working","rest","blocked"]):
        g = Image.open(f"{B}/mods/oompa-agents/sprites/{j}-{st}.gif")
        frames = [f.convert("RGBA") for f in ImageSequence.Iterator(g)]
        sheet.alpha_composite(frames[0], (i*160+8, k*200))
        if st == "working":
            sheet.alpha_composite(frames[3], (i*160+8, 600 + 0))
    p = Image.open(f"{B}/mods/oompa-agents/art/{j}.png").convert("RGBA")
    sheet.alpha_composite(p, (i*160+40, 820))
x = 8
for r in ["waterfall","factory","inventing","orchard"]:
    sheet.alpha_composite(Image.open(f"{B}/mods/oompa-spaces/art/{r}.png").convert("RGBA"), (x, 920)); x += 90
for k in ["files","changes","inbox"]:
    sheet.alpha_composite(Image.open(f"{B}/mods/oompa-tabs/art/{k}.png").convert("RGBA"), (x, 935)); x += 60
sheet.save(out)
