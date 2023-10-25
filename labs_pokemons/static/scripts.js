function myFunction(pokemonName) {
        // Загрузка данных из JSON файла
        fetch('pokemon/'+pokemonName)
            .then(response => response.json())
            .then(data => {
                // Нахождение покемона по имени в загруженных данных
                const pokemon = data.find(p => p.name === pokemonName);
                if (pokemon) {
                    // Отображение полной информации о покемоне
                    //console.log(pokemon);
                    // Получаем модальное окно
                    var modal = document.getElementById("exampleModal");
                     // Находим элементы модального окна, в которые нужно вставить информацию о покемоне
                    var modalTitle = modal.querySelector(".modal-title");
                    var modalBody = modal.querySelector(".modal-body");
                    // Вставляем информацию о покемоне в элементы модального окна
                    modalTitle.textContent = pokemon.name;
                    modalBody.innerHTML = "<h5>Скорость: " + pokemon.speed + "</h5><h5>Защита: " + pokemon.defense + "</h5>" +
                        "<h5>Атака: " + pokemon.attack + "</h5><h5>HP: " + pokemon.hp + "</h5><h5>Вес: " + pokemon.weight + "</h5>" +
                        "<h5>Спец.Защита: " + pokemon.special_defense + "</h5><h5>Спец.атака: " + pokemon.special_attack + "</h5>";

                    // Открываем модальное окно
                    var modalBS = bootstrap.Modal.getInstance(modal);
                    modalBS.show();
                } else {
                    console.log('Покемон не найден');
                }
            })
            .catch(error => console.log(error));
    };


    function savePokemonName(name,image_url, defense, attack) {
        localStorage.setItem('name', name);
        localStorage.setItem('image_url', image_url);
        localStorage.setItem('defense', defense);
        localStorage.setItem('attack', attack);

    }