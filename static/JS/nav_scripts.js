$(function () {
  AOS.init();
    $(document).scroll(function () {
      var $nav = $(".fixed-top");
      $nav.toggleClass("scrolled", $(this).scrollTop() > $nav.height());
    });
  });
  function gradeConv(mark) {
    grade = ""
    if (mark <= 100 && mark >= 90)
      grade = "A+"
    else if (mark <= 89 && mark >= 85)
      grade = "A"
    else if (mark <= 84 && mark >= 80)
      grade = "A-"
    else if (mark <= 79 && mark >= 75)
      grade = "B+"
    else if (mark <= 74 && mark >= 70)
      grade = "B"
    else if (mark <= 69 && mark >= 65)
      grade = "B-"
    else if (mark <= 64 && mark >= 60)
      grade = "C+"
    else if (mark <= 59 && mark >= 55)
      grade = "C"
    else if (mark <= 54 && mark >= 50)
      grade = "D+"
    else if (mark <= 49 && mark >= 40)
      grade = "D"
    else
      grade = "F"
    return grade
  } function cgpaConv(mark) {
    cgpa = 0
    if (mark <= 100 && mark >= 90)
      cgpa = 4.00
    else if (mark <= 89 && mark >= 85)
      cgpa = 3.75
    else if (mark <= 84 && mark >= 80)
      cgpa = 3.50
    else if (mark <= 79 && mark >= 75)
      cgpa = 3.25
    else if (mark <= 74 && mark >= 70)
      cgpa = 3.10
    else if (mark <= 69 && mark >= 65)
      cgpa = 3.00
    else if (mark <= 64 && mark >= 60)
      cgpa = 2.75
    else if (mark <= 59 && mark >= 55)
      cgpa = 2.50
    else if (mark <= 54 && mark >= 50)
      cgpa = 2.25
    else if (mark <= 49 && mark >= 40)
      cgpa = 2.00
    else
      cgpa = -99999990.00
    return cgpa
  }