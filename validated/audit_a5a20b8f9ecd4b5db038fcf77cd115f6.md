### Title
Webhook tenant identity (`shop` header) is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, but the `shop` (tenant) that the webhook is attributed to is read from a separate, unsigned HTTP header. Any caller who can produce one valid `(body, hmac)` pair — trivially available to any developer/merchant who has installed the app on their own store, since the HMAC secret (`api_secret_key`) is the same across all shops for a given app — can replay that exact body/HMAC pair to the app's public webhook endpoint while substituting an arbitrary `shop-domain` header, causing the app to process the payload as if it came from a different (victim) tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` are all pulled from separate, non-HMAC-covered headers: [2](#0-1) 

`Registry.process` verifies only that the body's HMAC is valid, then immediately trusts `request.shop` (and the other headers) to build the tenant-identifying `WebhookMetadata` that gets handed to the host app's handler: [3](#0-2) 

`Utils::HmacValidator.validate` computes and compares the HMAC using only `verifiable_query.to_signable_string` (the raw body) against `Context.api_secret_key`: [4](#0-3) 

The identity binding that should hold is:
`HMAC(api_secret_key, raw_body)` proves `raw_body` is unmodified **and** originates from Shopify, but it says nothing about which shop the payload was sent for. The code however treats `hmac_valid? == true` as proof of `(body, shop) == (verified_body, attributed_shop)`. Because `api_secret_key` is one value shared across every shop that has installed the app (it is the app's client secret, not a per-shop secret), any attacker who is themselves a legitimate merchant installer of the app can observe/receive a genuine webhook (or hand-craft a body and let their own store's Shopify webhook delivery sign it) with a valid HMAC, then resend that exact `raw_body` + `X-Shopify-Hmac-Sha256` pair to the app's public webhook endpoint with the `X-Shopify-Shop-Domain` header changed to a victim shop's domain. `Utils::HmacValidator.validate` will report success (it only checks the body signature), and `Registry.process` will hand the handler a `WebhookMetadata` claiming `shop: <victim shop>` with attacker-controlled `body`/`topic`.

This is the direct analog of the reported bug class ("a field acted on but not covered by the HMAC"): here the `shop` tenant identifier is acted upon (used to dispatch/attribute the webhook) without being bound into the same HMAC used to authenticate the request.

### Impact Explanation
If a host application uses `data.shop` from `WebhookMetadata` to look up the tenant's session/access token or to write/mutate tenant-scoped state (a documented and expected usage pattern — see `docs/usage/webhooks.md` example `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`), an attacker can inject arbitrary attacker-chosen webhook `body` content attributed to an arbitrary victim shop domain. This is a cross-tenant integrity/confusion issue: the attacker doesn't need any credential belonging to the victim, only the ability to install the app once on any shop of their own (a normal unprivileged action) to obtain a validly-signed body/HMAC pair, and network access to the app's webhook endpoint.

### Likelihood Explanation
The `api_secret_key` HMAC is shared across all installations of the app, so any merchant/attacker who installs the app can trivially obtain a genuine `(body, hmac)` pair. Combining that with an arbitrary `X-Shopify-Shop-Domain` header requires nothing more than an unauthenticated POST to the app's public webhook route, which is by design internet-reachable. No secrets, tokens, or privileged access are required beyond normal app installation.

### Recommendation
Bind the tenant/shop identity into the value that is HMAC-authenticated, or otherwise cryptographically/authoritatively verify that the `shop` header corresponds to the same request that produced the signed body — e.g., include the shop domain in the signable string, or require the caller to have a valid, previously-registered webhook-to-shop mapping and cross-check the delivered `shop` against Shopify's known registration for that specific webhook subscription/`webhook_id`, rather than trusting the unauthenticated header outright.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`, triggering Shopify to deliver a real webhook (e.g. `orders/create`) to the app's endpoint with a valid `X-Shopify-Hmac-Sha256` header computed over the raw JSON body using the app's shared `api_secret_key`.
2. Attacker captures this `raw_body` and its accompanying `hmac` header value.
3. Attacker sends a new HTTP POST to the same public webhook endpoint, reusing the identical `raw_body` and `X-Shopify-Hmac-Sha256` header, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Utils::HmacValidator.validate` succeeds because it only checks the body's HMAC (`lib/shopify_api/utils/hmac_validator.rb:26-31`), which is unchanged.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) invokes the app's handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: <attacker-controlled>, ...)`, and any host-app logic keyed on `data.shop` acts on behalf of the victim tenant using attacker-supplied data.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
