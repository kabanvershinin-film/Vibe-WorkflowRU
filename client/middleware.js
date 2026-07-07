import { NextResponse } from 'next/server'

export function middleware(request) {
  const apiUrl = process.env.API_URL || 'http://localhost:8000'
  const requestHeaders = new Headers(request.headers)
  requestHeaders.set('x-middleware-cache', 'no-cache')

  if (request.nextUrl.pathname.startsWith('/api/')) {
    const newUrl = new URL(request.nextUrl.pathname + request.nextUrl.search, apiUrl)
    return NextResponse.rewrite(newUrl, {
      request: {
        headers: requestHeaders,
      },
    })
  }

  return NextResponse.next()
}

export const config = {
  matcher: '/api/:path*',
}
