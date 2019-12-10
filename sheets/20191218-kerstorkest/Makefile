CMD=../../spec2sheet.py
TARGET= \
	wijkomentezamen.pdf \
	stillenacht.pdf \
	nuzijtwellekome.pdf \
	gloria.pdf \
	winternacht-melodie.pdf \
	winternacht-akkoorden.pdf \
	vrolijkkerstfeest.pdf \
	herdertjes.pdf

all: $(TARGET)

%.pdf: %.svg
	inkscape $< --export-pdf=$(@:.pdf=-cymbaal.pdf)
	lilypond --output=$(@:.pdf=-ly) $(@:.pdf=.ly)
	pdfunite $(@:.pdf=-cymbaal.pdf) $(@:.pdf=-ly.pdf) $@

wijkomentezamen.svg: wijkomentezamen.ly
	$(CMD) --scale=.6 --shift=0.03 --title="" $<

stillenacht.svg: stillenacht.ly
	$(CMD) --scale=.75 --shift=0 --title="Stille nacht" $<

nuzijtwellekome.svg: nuzijtwellekome.ly
	$(CMD) --scale=.63 --shift=-.01 --title="" $<

gloria.svg: gloria.ly
	$(CMD) --scale=.6 --shift=0.025 --title="" $<

winternacht-melodie.svg: winternacht-melodie.ly
	$(CMD) --scale=.87 --shift=.01 --title="Midden in de winternacht" $<

winternacht-akkoorden.svg: winternacht-akkoorden.ly
	$(CMD) --scale=.64 --shift=-.02 --title="Midden in de winternacht" $<

vrolijkkerstfeest.svg: vrolijkkerstfeest.ly
	$(CMD) --scale=.73 --shift=-.07 --title="Vrolijk kerstfeest" $<

herdertjes.svg: herdertjes.ly
	$(CMD) --scale=.56 --shift=-.01 --title="De herdertjes..." $<

clean:
	rm -f $(TARGET) $(TARGET:.pdf=-cymbaal.pdf) $(TARGET:.pdf=-ly.pdf) $(TARGET:.pdf=.svg)
