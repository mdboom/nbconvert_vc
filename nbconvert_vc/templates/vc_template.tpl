{% extends "null.tpl" %}

{% block markdowncell scoped %}
- markdown:
{{ cell.source | indent }}
{% endblock markdowncell %}

{% block input %}
- input:
{{ cell.source | ipython2python | indent }}
{% endblock input %}
