Confirmed: the analysis is complete. The `shop` field is read from the `x-shopify-shop-domain` header but is never included in the HMAC-signed content, which is only the raw body [1](#0-0) . The `Registry.process` method validates the HMAC and, if it passes, unconditionally trusts `request.shop` (and `request.topic`) to construct `WebhookMetadata` passed to the app's handler [2](#0-1) . `WebhookMetadata` carries `shop` as a plain field with no cryptographic binding [3](#0-2) .

### Title
Webhook shop-domain header is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content solely from the raw HTTP body (`to_signable_string` returns `@raw_body`), while the `shop` (and `topic`, `webhook_id`, `api_version`) values are read directly from HTTP headers that are excluded from the signature. `Registry.process` verifies only that the body's HMAC is valid for the configured `api_secret_key`, then forwards the unauthenticated `shop` header value to the app's `WebhookHandler` as if it were verified. This breaks the intended identity binding: `HMAC-verified bytes == raw_body`, but `shop used by handler == header value`, i.e. the equality `verified_bytes == acted_upon_shop` does not hold.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [4](#0-3) , and `Utils::HmacValidator.validate` computes/compares the HMAC over exactly that signable string [5](#0-4) . Meanwhile `Request#shop` is taken verbatim from the `shopify-shop-domain`/`x-shopify-shop-domain` header, entirely outside the signed content [6](#0-5) .

`Registry.process` raises only if the HMAC over the body fails; if it succeeds, it builds `WebhookMetadata` using the unauthenticated `request.shop` (and `request.topic`) and calls the registered handler with it [2](#0-1) . Since Shopify signs webhooks with a single `api_secret_key` per app (shared across every shop that installs the app), a valid `(raw_body, hmac)` pair is not shop-specific — it is valid for whatever `shop` header accompanies it. Any actor able to obtain one genuine `(body, hmac)` pair (trivially, by installing the app on their own shop and receiving a real webhook) can replay that exact body and signature to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header. `Registry.process` will accept it as valid and dispatch to the handler with the attacker-chosen `shop`, even though that shop never sent the webhook.

This is the same bug class as the report's core theme — a value acted upon by downstream logic that is not actually covered by the cryptographic check meant to authenticate it (there, royalties subtracted after the quote was verified; here, the `shop` identity used by the handler after the HMAC was verified).

### Impact Explanation
This crosses a tenant boundary: applications built on this gem commonly key stored state (sessions, offline tokens, feature flags, uninstall bookkeping) by `shop`. A forged `shop` value delivered through a legitimately-signed body lets an attacker who controls an installation of the target app on their own store trigger the handler logic attributed to an arbitrary victim shop — e.g., replaying a captured `app/uninstalled` or `shop/redact` webhook body with the victim's domain to make the app treat the victim as uninstalled/redacted, or to poison shop-scoped state the handler writes based on `data.shop`. This is a cross-tenant access impact under the rubric.

### Likelihood Explanation
Exploitation only requires an unprivileged actor who can install the target app on any shop they control (a normal, unprivileged action) to capture one legitimate `(raw_body, hmac)` pair for a webhook topic of interest, then replay it against the same app's public webhook endpoint with a different `shop` header. No access token, `api_secret_key`, or victim credentials are required — the signature validity is independent of which shop's domain is asserted.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the value that is HMAC-verified, or otherwise cryptographically/contextually bind `request.shop` before it is trusted — e.g., have `Registry.process` cross-check `request.shop` against session/store state known independently of the header, or require callers to pass the expected shop and compare it, rejecting mismatches. At minimum, document that `request.shop` is unauthenticated and must not be used for authorization decisions without independent verification.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a normal unprivileged action) and configures a webhook handler capture point, or intercepts their own app-received webhook traffic to obtain a real `(raw_body, x-shopify-hmac-sha256)` pair for a topic such as `app/uninstalled`.
2. Attacker sends a POST to the app's public webhook endpoint with the exact captured `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and `x-shopify-topic` as needed.
3. `ShopifyAPI::Utils::HmacValidator.validate` succeeds because it only checks `raw_body` against the shared `api_secret_key` [7](#0-6) .
4. `Registry.process` dispatches to the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` [2](#0-1) , causing the app to perform shop-scoped side effects (e.g., session/token cleanup, data deletion, state changes) against the victim shop that the victim never authorized.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
