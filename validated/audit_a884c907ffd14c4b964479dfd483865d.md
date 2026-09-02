## Title
Webhook cross-tenant spoofing via unauthenticated `shop-domain` header — ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable payload from the raw request body only, while the `shop` (merchant identity) is read from a separate, unsigned header. `ShopifyAPI::Webhooks::Registry.process` then hands that unauthenticated `shop` value straight to the app's webhook handler. Because Shopify signs webhooks with the app's single, shop-independent `client_secret`, any shop that installs the app receives a batch of validly-signed `(body, hmac)` pairs it can freely replay to the app's public webhook endpoint with a different `shop-domain` header, causing the handler to process attacker-controlled data under an arbitrary victim shop's identity.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read from the `shop-domain` header, which is not part of that signable string: [2](#0-1) 

`Utils::HmacValidator.validate` only ever verifies `verifiable_query.to_signable_string` (i.e. the body) against the HMAC: [3](#0-2) 

`Registry.process` treats a passing HMAC check as full authentication of the request, then forwards the unauthenticated `request.shop` to the handler as the merchant identity: [4](#0-3) 

The equality that should hold is: `shop` bound in the HMAC == `shop` acted upon by the handler. Here, the HMAC only certifies "some request body was produced with knowledge of the app's `client_secret`" — it says nothing about which shop the request pertains to. Since Shopify signs webhooks with the app-wide `api_secret_key` (identical across every shop that installs the app), an unprivileged internet user who installs the app for their own store legitimately receives a stream of valid `(raw_body, hmac)` pairs. They can then POST that exact body/HMAC pair to the app's public webhook endpoint again, this time substituting the `x-shopify-shop-domain` header for a victim shop's domain. `Registry.process` will accept it as valid and invoke the handler with `shop: <victim_domain>` and `body: <attacker-controlled content>`.

### Impact Explanation
This breaks the tenant isolation the HMAC check is supposed to guarantee. Any webhook handler built on this library that trusts `data.shop` as an authenticated merchant identity (e.g., to look up/update per-shop records, react to `app/uninstalled` for token cleanup, or persist inbound order/customer data) can be tricked into applying attacker-supplied data to a victim shop's tenant. This is a cross-tenant access vulnerability rooted entirely in this gem's own webhook verification logic (`lib/shopify_api/webhooks/request.rb` and `lib/shopify_api/webhooks/registry.rb`), not in host-application misuse — the library exposes the unauthenticated header value under a same API surface (`WebhookMetadata#shop`) as if it were verified.

### Likelihood Explanation
Requires no access to `api_secret_key` or `access_token`, no privileged account, and no TLS interception. The only prerequisite is that the app be installable by arbitrary internet users (as most public/free-to-install Shopify apps are) and that it register at least one webhook topic. Obtaining a valid `(body, hmac)` sample is trivial — it's exactly what the attacker legitimately receives when the app processes their own store's events; capturing one delivery is enough to replay indefinitely with any shop domain.

### Recommendation
Either (a) require the caller to supply the destination/expected shop out-of-band and assert it equals `request.shop` before trusting it, and/or (b) bind `shop` (and `topic`) into the value verified by the HMAC (e.g., maintain a per-shop registry of installed shops and reject webhooks whose `shop` isn't recognized as installed with an active session), so a replayed payload cannot be revalidated for a different tenant. At minimum, document in `Registry.process`/`WebhookMetadata` that `shop` is unauthenticated and must be cross-checked against known installed shops by the consuming application before use.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and registers/receives any webhook (e.g. `orders/create`).
2. Shopify sends the app: `raw_body = B`, header `x-shopify-hmac-sha256 = HMAC(client_secret, B)`, header `x-shopify-shop-domain = attacker-shop.myshopify.com`.
3. Attacker resends the identical `raw_body B` and identical `hmac` value directly to the app's public webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses this fine (all required headers present); `Utils::HmacValidator.validate` succeeds because it only checks `B` against the HMAC.
5. `Registry.process` invokes the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the host app to process attacker-supplied content as if it originated from the victim shop.

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
