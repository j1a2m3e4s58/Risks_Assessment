from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse
import csv
from .models import RiskAssessment

@login_required
def dashboard(request):
    risks = RiskAssessment.objects.all().order_by('-created_at')
    
    # --- Matrix Helper Logic ---
    # We define the order of rows (Probability) and columns (Impact)
    # This matches the Excel standard: High Prob at top, High Impact at right.
    probabilities = ['Very High', 'High', 'Medium', 'Low', 'Very Low']
    impacts = ['Very Low', 'Low', 'Medium', 'High', 'Very High']

    def get_matrix_counts(risk_type):
        """
        Counts how many risks exist for every combination of Prob/Impact.
        risk_type is either 'inherent' or 'residual'.
        """
        # Initialize a 5x5 grid with zeros
        matrix_grid = {p: {i: 0 for i in impacts} for p in probabilities}
        
        # Count the actual risks
        for r in risks:
            if risk_type == 'inherent':
                p, i = r.inherent_probability, r.inherent_impact
            else:
                p, i = r.residual_probability, r.residual_impact
            
            if p in matrix_grid and i in matrix_grid[p]:
                matrix_grid[p][i] += 1
        return matrix_grid

    # Get the data for our two dynamic matrices
    inherent_data = get_matrix_counts('inherent')
    residual_data = get_matrix_counts('residual')

    # Calculate Totals for the top cards
    total_risks = risks.count()
    critical_risks = risks.filter(residual_rating='Critical').count()

    context = {
        'risks': risks,
        'total_risks': total_risks,
        'critical_risks': critical_risks,
        'user': request.user,
        
        # Pass the Matrix Data
        'probabilities': probabilities,
        'impacts': impacts,
        'inherent_matrix': inherent_data,
        'residual_matrix': residual_data,
    }
    return render(request, 'risks/dashboard.html', context)

# (Keep your export_risks_csv function exactly the same as before)
@login_required
def export_risks_csv(request):
    # ... (Keep existing code) ...
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="risk_register.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Description', 'Inherent Rating', 'Residual Rating'])
    for risk in RiskAssessment.objects.all():
        writer.writerow([risk.reference_id, risk.description, risk.inherent_rating, risk.residual_rating])
    return response