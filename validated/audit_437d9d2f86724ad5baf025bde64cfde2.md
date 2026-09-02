This confirms the vulnerability. The webhook HMAC in `Utils::HmacValidator.validate` is computed only over `Request#to_signable_string`, which returns `@raw_body` [1](#0-0) . The `shop` field, however, is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, entirely outside the HMAC-signed payload [2](#0-1) . `Registry.process` validates the HMAC and then hands the header-derived, unauthenticated `shop` value straight to the app's webhook handler as the tenant identity for the event [3](#0-2) .

### Title
Webhook shop-domain header is not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so the HMAC signature that `Utils::HmacValidator.validate` checks binds solely to the JSON body bytes. The `shop` (tenant identity), `topic`, `api_version`, and `webhook_id` values are all read from separate HTTP headers that are never included in the signed string, so they carry no cryptographic binding to the HMAC at all.

### Finding Description
`Utils::HmacValidator.validate` calls `verifiable_query.to_signable_string` to compute the expected signature and compares it against the `hmac` field [4](#0-3) . For `Webhooks::Request`, `to_signable_string` is defined to return `@raw_body` only [1](#0-0) , while `shop` is derived independently from the `shopify-shop-domain` (or `x-shopify-shop-domain`) header [2](#0-1) .

This breaks the identity binding: `hmac verified over raw_body` ≠ `shop used to process/attribute the event`. An unprivileged party who can obtain any body+HMAC pair that is valid for the app's secret (e.g., by receiving a legitimate webhook to their own installed shop, since the request body for many topics — like `app/uninstalled`, or any topic whose payload is shop-independent/predictable — doesn't itself encode the sender's shop) can replay that same raw body while substituting an arbitrary `shopify-shop-domain` header value. `Utils::HmacValidator.validate(request)` still returns `true` because the signature only ever verified the body bytes, never the shop header [5](#0-4) . `Registry.process` then forwards this forged, header-derived `shop` straight into `WebhookMetadata` passed to the app's handler [6](#0-5) , so the app attributes the (attacker-controlled) event to whatever shop the attacker names in the header — including shops the attacker does not control.

### Impact Explanation
This is a cross-tenant identity-binding break: the HMAC proves only that "some request with this body bytes was signed with the app secret," but the app's webhook handler trusts the unauthenticated `shop` header to decide which merchant's data/state the event affects. Depending on how the host app's `WebhookHandler#handle` implementation uses `data.shop` (e.g., to look up/mutate per-shop records, trigger per-shop side effects, or invalidate/rotate per-shop state), an attacker can inject events attributed to a victim shop, causing cross-tenant data corruption or unauthorized actions against a shop the attacker does not own.

### Likelihood Explanation
Any developer/merchant who can install the app on their own shop can obtain genuine, validly-HMAC-signed webhook deliveries. For topics whose body content is not shop-specific (or is otherwise attacker-influenced, e.g. via product/order data they control on their own shop), they can replay that exact body against the app's webhook endpoint while swapping only the `shop`-domain header, and the gem's `Utils::HmacValidator.validate` will accept it as authentic.

### Recommendation
Include the `shop`, `topic`, `api_version`, and `webhook_id` header values in the signable string (or otherwise bind them to the HMAC-verified payload), analogous to how `Oauth::AuthQuery#to_signable_string` includes all fields (`code`, `host`, `shop`, `state`, `timestamp`) that participate in the signature [7](#0-6) . At minimum, `Webhooks::Request#to_signable_string` should not allow `shop` to be trusted for tenant attribution unless it is cryptographically bound to the same signature that authenticates the body.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; trigger a webhook whose topic/body does not embed the shop name in a way that changes the raw bytes needed (or use a topic with attacker-controlled payload content), capturing the raw POST body `B` and the valid `x-shopify-hmac-sha256` header `H` that Shopify computed with the app's real secret.
2. Replay a POST to the app's webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` (unchanged), but `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: ...)` builds a `Request` whose `hmac` is `H` and whose `to_signable_string` is `B` [8](#0-7) .
4. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `B` only, matches `H`, and returns `true` [5](#0-4) .
5. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: ..., ...)`, so the app processes/attributes attacker-supplied data as belonging to `victim.myshopify.com` [6](#0-5) .

### Citations

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
