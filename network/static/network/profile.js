document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('#follow-btn') !== null ) {
        document.querySelector('#follow-btn').addEventListener('click', followUser);
    }

    let likeButtons = document.querySelectorAll('.like-btn')
    Array.prototype.forEach.call(likeButtons, (el) =>
        el.addEventListener('click', likePost)
    )
})


function followUser() {
    let idToFollow = document.querySelector('#follow-btn').getAttribute('data-follow');
    console.log(idToFollow);
    fetch('follow/' + idToFollow)
        .then(response => response.json())
        .then(data => {
            console.log(data);
            document.querySelector('#followers').innerHTML = 'Followers: ' + data.followers;
            if (data.unfollowed === true) {
                document.querySelector('#follow-btn').value = 'Follow';
                document.querySelector('#follow-btn').classList.add('btn-success');
                document.querySelector('#follow-btn').classList.remove('btn-danger');
            } else {
                document.querySelector('#follow-btn').value = 'Unfollow';
                document.querySelector('#follow-btn').classList.add('btn-danger');
                document.querySelector('#follow-btn').classList.remove('btn-success');
            }
        })
}

function likePost(e) {
    console.log(e.target);
    let idToFollow = e.target.getAttribute('data-post-id');
    fetch('/likes/' + idToFollow)
        .then(response => response.json())
        .then(async data => {
            // await new Promise(r => setTimeout(r, 500));
            e.target.parentElement.lastElementChild.innerHTML = data.likes;
            if (data.created === true) {
                // change icon
                e.target.setAttribute("name", "heart")
            } else {
                e.target.setAttribute("name", "heart-outline")
            }
        })
}
