This confirms the finding. The webhook signature verification is scoped exclusively to the raw request body, while the `shop` (tenant identity) used downstream is taken from an unauthenticated header.

### Title
Webhook HMAC does not bind the `shop-domain` header, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` implements `VerifiableQuery` but its `to_signable_string` returns only the raw HTTP body [1](#0-0) , while the `shop` accessor used to identify the tenant is read directly from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header [2](#0-1) . `HmacValidator.validate` only checks the HMAC over `to_signable_string` (the body) [3](#0-2) , and `Registry.process` dispatches to the app's handler using `request.shop` after that validation succeeds [4](#0-3) .

### Finding Description
The binding that should hold is: `hmac_verified_bytes == bytes_that_determine_the_tenant`. Here that equality is broken — the HMAC is computed and verified solely over `@raw_body`, and `shop-domain` is never part of the signable string. Since the same `api_secret_key` is used to sign every webhook regardless of which shop triggered it (it's the app's single client secret, not a per-shop secret), any HMAC value that is valid for one shop's webhook body is equally valid for that same body under a spoofed `shop-domain` header. An attacker who can obtain (e.g., via a public webhook proxy, logging endpoint, or by triggering a webhook on their own shop with attacker-controlled body content) any single valid `(raw_body, hmac)` pair can resend it to the app's webhook endpoint with an arbitrary `x-shopify-shop-domain` header value. `HmacValidator.validate` will report success because it never inspects the shop header, and `Registry.process` will hand `WebhookMetadata` with the attacker-chosen `shop` to the app's handler [5](#0-4) .

### Impact Explanation
This breaks the tenant/shop identity boundary: the app processes a webhook "as" a different shop than actually sent it. Depending on how the host app's `WebhookHandler` implementations use the `shop` field (e.g., to look up/update per-tenant data, invalidate sessions, or fulfil `customers/redact`/`shop/redact` compliance webhooks), this enables cross-tenant data corruption or confusion — for example, forging a `shop/redact` or `customers/data_request` webhook against a victim shop, or injecting attacker-controlled body content that the app associates with a victim's shop record. This matches the Critical-severity "cross-tenant access" category.

### Likelihood Explanation
Exploitation requires obtaining one genuine `(body, hmac)` pair (an unprivileged attacker can generate this cheaply by installing/creating their own dev shop and triggering a webhook with a body of their choosing, or capturing a compliance webhook), then resending it with a different shop header — no access token, `api_secret_key`, or privileged account is required.

### Recommendation
Bind the shop identity into the verified signature space, matching Shopify's actual webhook HMAC contract only covers body — so instead, cross-check that `request.shop` corresponds to a shop this app instance actually has an active session/install for before dispatching, or require the transport layer (e.g., mutual TLS to Shopify) to be the sole source of shop attribution and never trust the header for authorization decisions without an independent installation-state check.

### Proof of Concept
1. App installed on `shop-a.myshopify.com`; attacker owns `shop-a` (their own dev store) and triggers any webhook (or crafts a raw body themselves and asks Shopify to send it) to capture a valid `(raw_body, x-shopify-hmac-sha256)` pair, computed with the app's shared `api_secret_key`.
2. Attacker POSTs to the app's webhook endpoint with the captured `raw_body` and `hmac` unchanged, but sets `x-shopify-shop-domain: shop-b.myshopify.com` (a victim shop also using the app).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which validates successfully since it only checks `raw_body` against the hmac [6](#0-5) .
4. The handler receives `WebhookMetadata` with `shop: "shop-b.myshopify.com"` even though the payload never originated from `shop-b`, allowing the attacker to influence app behavior/state tied to `shop-b`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
```
