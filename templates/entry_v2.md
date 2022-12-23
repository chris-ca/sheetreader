## Logbook
- **Tag**: #{{e.no}}
{% if e.is_cycling_day %}- **Unterwegs**: von {{e.start}}-{{e.end}} Uhr, Fahrzeit: {{e.time}} h
  - {{e.distance}} km (⌀ {{e.average_speed|round|int}} kph){% if e.elevation is not none %} ({{'{0:,}'.format(e.elevation| int) }} m up, {{'{0:,}'.format(e.descent| int) }} m down){% endif %}
  - **Gesamt**: {{e.km_cumulative}} km
{% endif %}- **Ort**: {{e.place}} ({{e.country}})
- **Unterkunft**: {{e.overnight}}{% if e.placeDetail %} ({{e.placeDetail}}){% endif %}{%if e.altitude %} ({{'{0:,}'.format(e.altitude| int) }} hm){%endif%}
- **Ausgaben**: {{e.cost_p_day|round|int}} €{%if e.food_cost > 0 %} (Essen {{e.food_cost|round|int}}){% endif %}{%if e.accommodation > 0 %} (Schlafen {{e.accommodation|round|int}}){% endif %}{%if e.other > 0 %} (Sonst. {{e.other|round|int}}){% endif %}
{% if e.summary != "" %}### Summary
{{e.summary}}
{% endif %}
{%- if e.internal_notes != "" -%}### Notes
{{e.internal_notes}}
{% endif %}
