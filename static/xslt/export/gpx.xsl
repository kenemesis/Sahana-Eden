<xsl:stylesheet version="1.0"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns="http://www.topografix.com/GPX/1/1"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
>
<xsl:output method="xml" indent="yes"/>
<xsl:template match="/sahanapy">
  <gpx creator="" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd" version="1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.topografix.com/GPX/1/1">
	<xsl:apply-templates select="resource"/>
  </gpx>
</xsl:template>
<xsl:template match="resource">
<xsl:if test="reference[@field='location_id']">
  <wpt>
	<xsl:attribute name="lat"><xsl:value-of select="reference[@field='location_id']/@lat"/></xsl:attribute>
	<xsl:attribute name="lon"><xsl:value-of select="reference[@field='location_id']/@lon"/></xsl:attribute>
    <name><xsl:value-of select="data[@field='name']"/></name>
	<desc><xsl:value-of select="reference[@field='organisation_id']"/> <xsl:value-of select="data[@field='type']"/></desc>
  </wpt>
</xsl:if>
</xsl:template>
</xsl:stylesheet>