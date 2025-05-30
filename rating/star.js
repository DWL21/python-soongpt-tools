const rows = document.querySelectorAll('tr');
const data = Array.from(rows).map(row => {
    const starElement = row.querySelector('a.star');
    const courseElement = row.querySelector('td.bold');
    const professorElement = courseElement?.nextElementSibling;
    const courseCodeElement = courseElement?.previousElementSibling;
    return {
        star: Number(starElement?.getAttribute('title')) ?? 0,
        course: courseElement?.textContent.trim() ?? "",
        professor: professorElement?.textContent.trim() ?? "",
        courseCode: courseCodeElement?.textContent.trim() ?? ""
    };
});

const jsonData = JSON.stringify(data);
console.log(jsonData);