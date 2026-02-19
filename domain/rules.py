import datetime
import calendar

def days_in_each_month(start_date: datetime.date, end_date: datetime.date):
    """
    Calculates the number of days in each month between two dates.

    Args:
        start_date (datetime.date): The start date of the period.
        end_date (datetime.date): The end date of the period.

    Returns:
        dict: A dictionary where keys are 'YYYY-MM' strings and values are the 
              number of days in that month within the date range.
    """

    days_per_month = {}
    # If start and end date are in same month/year then just return end day - start day
    if (start_date.month == end_date.month) and (start_date.year == end_date.year):
        month_key = f"{end_date.year}-{end_date.month:02d}"
        days_per_month[month_key] = end_date.day - start_date.day
        return days_per_month
    
    current_date = start_date

    while current_date <= end_date:
        year = current_date.year
        month = current_date.month
        
        # Get the total number of days in the current month, accounting for leap years.
        _, num_days_in_month = calendar.monthrange(year, month)
        
        # Determine the relevant days in the current month
        if current_date.year == start_date.year and current_date.month == start_date.month:
            # For the start month, days are from the start date to the end of the month
            days_count = num_days_in_month - start_date.day + 1
        elif current_date.year == end_date.year and current_date.month == end_date.month:
            # For the end month, days are from the start of the month to the end date
            days_count = end_date.day - 1
        else:
            # For full intermediate months, all days are counted
            days_count = num_days_in_month
        
        # Format the month as YYYY-MM
        month_key = f"{year}-{month:02d}"
        days_per_month[month_key] = days_count

        # Move to the first day of the next month
        if month == 12:
            current_date = datetime.date(year + 1, 1, 1)
        else:
            current_date = datetime.date(year, month + 1, 1)
            
    return days_per_month

def get_media_perm(proc_code: str, proc_list):
    for proc in proc_list:
        if proc.get('code') == proc_code:
            return proc.get('avrg_stay')

def calc_perm_maior(start: datetime.date, end: datetime.date, media_perm: int):
    return (end - start).days - media_perm