This confirms the finding: the webhook HMAC in `ShopifyAPI::Webhooks::Request` only signs the raw body (`to_signable_string` returns `@raw_body`), while `shop`, `topic`, and `webhook_id` are read straight from unauthenticated headers and passed on to the handler as trusted tenant identity.This confirms the finding: `Registry.process` explicitly documents that it "will verify the request did indeed come from Shopify," yet the verification only proves the raw body's integrity — the `shop` (tenant identity), `topic`, and `webhook_id` fields are read straight from unauthenticated HTTP headers and passed to the app's handler as trusted data [1](#0-0) , exactly the "field acted on but not covered by the HMAC" pattern from the LID-12 analog.

### Title
Webhook `shop` identity is not bound by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable content solely from the raw request body (`to_signable_string` returns `@raw_body`), while the `shop` (and `topic`/`webhook_id`) values used to identify the tenant are read directly from HTTP headers that are never included in the signed content. `ShopifyAPI::Webhooks::Registry.process` trusts `request.shop` as the tenant identity for the handler without any binding to the HMAC-verified bytes.

### Finding Description
`Request#hmac` reads `shopify-hmac-sha256`/`x-shopify-hmac-sha256`, and `Request#to_signable_string` returns only `@raw_body`: [2](#0-1) 

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)`, which computes `HMAC(api_secret_key, request.to_signable_string)` and compares it to `request.hmac` — i.e., it only proves the body bytes were signed with the app's secret: [3](#0-2) 

After this check passes, `Registry.process` builds `WebhookMetadata` directly from `request.shop`, `request.topic`, and `request.webhook_id` — fields taken from the `x-shopify-shop-domain`, `x-shopify-topic`, and `x-shopify-webhook-id` headers, none of which are part of the signed content: [1](#0-0) [4](#0-3) 

This breaks the intended identity binding: `HMAC_valid(body) == true` is treated as proof that `(shop, topic, body)` as a tuple came from Shopify for that specific shop, but the equality that is actually verified is only `HMAC(secret, body) == received_hmac`. The `shop` field is never part of what's cryptographically bound. The gem's own documentation states processing "will verify the request did indeed come from Shopify," which overstates what is actually checked — this mirrors the LID-12 pattern of trusting an unverified field (the max amount) instead of the verified return value; here the trusted-but-unverified field is the `shop` header.

Because the app's `api_secret_key` (`client_secret`) is shared across all shops that install the app, any merchant that has installed the app can, through normal usage, trigger webhook deliveries to the app's endpoint containing attacker-influenced body content (e.g., product/order fields) with a valid HMAC computed over that body using the shared secret. Since the header `x-shopify-shop-domain` is not part of the signed bytes, an attacker who controls the delivery target (i.e., replays or forges an HTTP POST directly to the app's public webhook endpoint, which by design must accept unauthenticated internet traffic from Shopify's infrastructure) can pair a validly-signed body with an arbitrary `shop-domain` header value, causing the app to process data under a different shop's identity.

### Impact Explanation
This crosses the "cross-tenant access" boundary in the Critical impact category: the webhook handler receives `WebhookMetadata.shop` as an authenticated tenant identifier while it is fully attacker-controllable independent of the HMAC. An application built on this gem that uses `data.shop` (as its own documentation examples do — `perform_later(topic: data.topic, shop_domain: data.shop, ...)`) to route webhook data into per-tenant storage would write or act on data under the wrong shop, or allow injecting events attributed to a victim shop, without ever needing access to that shop's credentials.

### Likelihood Explanation
Exploitability depends on the ability to reach the app's public webhook HTTP endpoint with a crafted body/HMAC pair and a spoofed `shop-domain` header — this endpoint is inherently internet-facing by design (Shopify calls it over HTTP), so no privileged access, TLS interception, or credential theft is required, only the ability to send an HTTP POST with a validly-signed body (obtainable via ordinary interaction as an app-installing merchant) and a different header value.

### Recommendation
Include `shop`, `topic`, and `webhook_id` (in addition to the raw body) in the HMAC-signed content when validating webhooks, or independently verify that the `shop` header corresponds to a shop with an active, registered webhook subscription for that `webhook_id`/topic before dispatching to the handler, so the tenant identity used by the handler is cryptographically bound to the verified request.

### Proof of Concept
1. App installs the gem's webhook `Registry.process` on a public endpoint, per the documented pattern in `docs/usage/webhooks.md`.
2. Attacker (a merchant who has legitimately installed the app on shop `attacker.myshopify.com`) triggers an event (e.g., updates a product) causing Shopify to deliver a webhook with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC(api_secret_key, B)` — this HMAC is valid because `api_secret_key` is the same for every shop that installed this app.
3. Attacker replays an HTTP POST directly to the app's webhook endpoint with the same body `B` and same `H`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `HmacValidator.validate` succeeds because it only checks `B` against `H`; `Registry.process` then calls the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, causing the app to process/store data as if it came from the victim shop.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
