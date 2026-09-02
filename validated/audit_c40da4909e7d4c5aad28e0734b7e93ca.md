Found the analog. `Webhooks::Request#to_signable_string` (the bytes covered by the HMAC) is `@raw_body` only, but `Registry.process` dispatches and authorizes the webhook using `request.shop` and `request.topic`, both of which come from the `x-shopify-shop-domain` / `x-shopify-topic` HTTP headers, which are **not** part of the HMAC-signed payload at all. [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Webhook `shop`/`topic` fields are not covered by the HMAC, allowing header-spoofed webhook dispatch - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body, while `shop` and `topic` (and `api_version`, `webhook_id`) are read straight from HTTP headers and never included in the HMAC-signed string. `Registry.process` validates the HMAC over the body only, then trusts the header-derived `shop`/`topic` to select the handler and populate `WebhookMetadata` passed to the app's handler.

### Finding Description
`Utils::HmacValidator.validate` calls `verifiable_query.to_signable_string` and compares its HMAC-SHA256 (keyed with `Context.api_secret_key`) against the value in the `x-shopify-hmac-sha256` header. [4](#0-3) 
For webhook requests, `to_signable_string` is defined as just `@raw_body`: [2](#0-1) 
Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are pulled directly from attacker-controllable HTTP headers (`x-shopify-shop-domain`, `x-shopify-topic`, etc.) with no cryptographic binding to those header values: [5](#0-4) 
`Registry.process` only verifies that the *body* HMAC is valid, then dispatches based on `request.topic` and forwards `request.shop` into the handler's `WebhookMetadata`: [3](#0-2) 

The equality that should hold is: `shop` and `topic` values trusted by the handler == `shop`/`topic` values verified by the HMAC. In this gem, the HMAC only proves the *body bytes* are authentic; it proves nothing about which `shop-domain` or `topic` header accompanied that body. An attacker who can reach the app's webhook endpoint (this is an unauthenticated, internet-facing endpoint by design) can replay a body/HMAC pair captured from a genuine webhook for shop A, but wrap it with a forged `x-shopify-shop-domain` header for shop B (or a different `x-shopify-topic`). `Utils::HmacValidator.validate` still passes because it only checks the body, and the handler receives `WebhookMetadata` claiming the request is `shop: B` (or a different topic) even though the signed content never attested to that shop or topic.

This is the same class of bug as the report: a value acted upon (`shop`, used as the tenant identifier passed to the handler) is not covered by the integrity check (HMAC over raw body only), enabling a cross-tenant/topic confusion analogous to using stale/unbound oracle data to compute a trusted result.

### Impact Explanation
This crosses a tenant-identity boundary: an app handler that keys behavior/storage by `WebhookMetadata#shop` (e.g., "look up merchant record for this shop and process the redact/data payload") can be made to process a legitimately-signed body under an attacker-chosen shop domain, since `shop` is never authenticated by the HMAC. Depending on how the host app trusts `shop`, this enables cross-tenant data confusion/injection into another merchant's webhook processing pipeline. This matches the High severity criteria (credential/tenant boundary crossed without requiring privileged secrets — the HMAC only requires knowledge of a previously observed valid body/HMAC pair, not the `client_secret` itself, and headers are fully attacker-controlled).

### Likelihood Explanation
Webhook receiver endpoints are unauthenticated, internet-reachable HTTP endpoints by design (that's the whole point of `Webhooks::Registry.process`), so an attacker can freely send arbitrary headers alongside any previously-seen (or otherwise obtained) valid `raw_body`/`hmac` pair. No secret knowledge is needed to manipulate the `shop`/`topic` headers — only the body and its accompanying HMAC need to be valid, and those can come from any real webhook delivery (e.g., one sent to the attacker's own store, replayed with a spoofed `shop` header pointing at a victim shop).

### Recommendation
Include `shop` (and ideally `topic`, `api_version`) in the signed payload verification, or otherwise cryptographically bind the header values to the signed body — e.g., require they match a separate signed claim, or reconstruct the signable string used elsewhere by Shopify to include these fields rather than trusting raw headers post-HMAC-check.

### Proof of Concept
1. Capture a legitimate webhook delivery: `raw_body = "{...genuine payload...}"`, `x-shopify-hmac-sha256 = valid_hmac`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`.
2. Replay the same `raw_body` and `x-shopify-hmac-sha256` to the app's webhook endpoint, but set `x-shopify-shop-domain: victim-shop.myshopify.com` (and/or a different registered `x-shopify-topic`).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only hashes `@raw_body` — validation succeeds. [6](#0-5) 
4. The handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` where `shop` is the attacker-forged `victim-shop.myshopify.com`, despite the signed body never having attested to that shop. [7](#0-6)

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
