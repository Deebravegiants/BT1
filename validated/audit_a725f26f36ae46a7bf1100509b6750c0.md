### Title
Webhook `shop-domain` header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `ShopifyAPI::Webhooks::Registry.process` trusts the unsigned `shop-domain` header to identify which tenant a webhook belongs to. Because the HMAC never covers the shop identifier, an attacker who legitimately receives one valid webhook (with a valid signature) for their own store can replay the exact same body/HMAC pair while swapping the `X-Shopify-Shop-Domain` header to a victim shop, and the signature check still passes.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 

Only `@raw_body` is signed. The `shop` accessor pulls the tenant identity from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is completely independent of the signed bytes: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately hands `request.shop` (and `request.topic`, `request.webhook_id`) to the host app's handler as trusted tenant context, without any additional binding check: [3](#0-2) 

`HmacValidator.validate` (used here) only ever checks `compute_signature(verifiable_query.to_signable_string, secret)` against the received `hmac`: [4](#0-3) 

This is the same root cause class as the referenced report: a value that is *acted upon* (here, the tenant/shop that the webhook payload gets attributed to) is not bound by the same authentication mechanism (HMAC) that is used to establish trust in the request. The equality that should hold is:

`shop_used_by_handler == shop_that_the_HMAC_actually_authenticates`

but in this code the right-hand side doesn't exist — the HMAC authenticates only the body bytes, never the shop.

### Impact Explanation
Any entity capable of receiving one legitimately signed webhook delivery for their own shop (e.g., a malicious merchant who has installed the app, which is an "unprivileged" party from the perspective of any other tenant of the multi-tenant app) can capture that raw body + HMAC and replay it to the app's webhook endpoint with the `shop-domain` header rewritten to point at a different, victim shop. Since the signature only covers `raw_body`, the replayed request still passes `HmacValidator.validate`, and `Registry.process` will dispatch the handler with `shop: <victim-shop>` and the attacker-controlled body. Depending on what the host app's handler does with `WebhookMetadata#shop` (e.g. writing/deleting data keyed by shop, or fulfilling GDPR-style `customers/redact` / `shop/redact` mandatory webhooks), this results in cross-tenant data corruption or spoofed compliance actions attributed to a shop that never sent them — a cross-tenant integrity/confidentiality boundary crossing.

### Likelihood Explanation
The attacker only needs to install the app on their own store (or otherwise legitimately receive one webhook) and capture the raw HTTP request/response — no access to `api_secret_key`, access tokens, or any other credential is required, and no TLS interception or social engineering is needed since the attacker owns and receives that traffic themselves. The replay is a trivial header rewrite against a public HTTP endpoint the app exposes for webhook delivery.

### Recommendation
Bind the shop (and topic/webhook id) into the authenticated material, e.g. by including the `shop-domain` header (and ideally topic/webhook-id) in the HMAC-signed string similarly to how `Auth::Oauth::AuthQuery#to_signable_string` binds `shop` into its signable string, or by having the host app cross-check `request.shop` against the tenant that installed the app for the given webhook topic before trusting the payload. At minimum, document that consumers of `WebhookMetadata#shop` cannot treat it as authenticated and must independently verify shop ownership.

### Proof of Concept
1. App-installer A subscribes to a webhook topic and receives a legitimate delivery: body `B`, header `X-Shopify-Hmac-Sha256: H` (valid for `B`), `X-Shopify-Shop-Domain: a-shop.myshopify.com`.
2. A replays the exact same request to the app's webhook endpoint but changes only `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: ...)` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `B` only (per `to_signable_string`) — it matches `H`, so validation succeeds.
4. `Registry.process` invokes the registered handler with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the host app to act on victim-shop's tenant data using attacker-controlled body content, despite the HMAC never having authenticated the shop field.

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
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
