const d3 = Object.assign(
  {},
  require('d3-selection'),
  require('d3-transition'),
);

const stack = {};

const startLoading = (selector) => {
  stack[selector] = stack[selector] || [];
  if (!stack[selector].length) {
    d3.selectAll(selector)
      .style('display', null)
      .transition()
      .style('opacity', 1);
  }
  stack[selector].push(undefined);
};

const stopLoading = (selector) => {
  stack[selector].pop();
  if (!stack[selector].length) {
    d3.selectAll(selector)
      .transition()
      .style('opacity', 0)
      .on('end', function() {
        d3.select(this).style('display', 'none');
      });
  }
};

export {
  startLoading,
  stopLoading,
}
