### Title
Webhook shop identity is not bound by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, never including the `shop-domain` header. `ShopifyAPI::Webhooks::Registry.process` validates that HMAC and then unconditionally trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler. Because Shopify apps use a single `api_secret_key` shared across every installed shop, a valid `(raw_body, hmac)` pair obtained for one shop (e.g. the attacker's own trial/dev store) remains cryptographically valid when replayed with a different `shop-domain` header, letting an unprivileged party impersonate webhook traffic from a victim shop.

### Finding Description
The signable string for a webhook request is defined as just the raw body: [1](#0-0) 

The `shop` accessor is read straight from the (unauthenticated) `shop-domain`/`x-shopify-shop-domain` header, and is not part of `to_signable_string`: [2](#0-1) 

`Registry.process` validates only the HMAC of the raw body, then hands `request.shop` straight to the registered handler as the trusted tenant identity: [3](#0-2) 

`HmacValidator.validate` confirms the signature against `Context.api_secret_key`, which is one single secret shared by the app across **all** shops that have it installed — it is not shop-specific: [4](#0-3) 

Because the signed bytes (`raw_body`) and the trusted identity field (`shop-domain` header) are disjoint, and the signing key is shop-agnostic, any body+HMAC pair valid for shop A is also a valid signature for the identical body claimed to be from shop B — the gem has no mechanism to detect the substitution. This breaks the intended binding: `shop-header-presented == shop-that-produced-the-HMAC`.

### Impact Explanation
An attacker who controls any shop where the target app is installed (even a free/trial store they legitimately own) can capture a real `(raw_body, x-shopify-hmac-sha256)` pair from their own webhook deliveries, then submit that exact body/HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `Registry.process` will pass HMAC validation and deliver the payload to the handler tagged with the victim's shop, via `WebhookMetadata#shop`. Any app logic that uses this field to select the shop record to update (order/webhook processing, `app/uninstalled` handling, data mutation, etc.) can be tricked into acting on the wrong tenant — a cross-tenant impact achievable by an unprivileged internet user who merely installed the app on their own store.

### Likelihood Explanation
Likelihood is Medium-to-High: no access token, `client_secret`, or privileged account is required — only the ability to install the target app on a store the attacker controls (trivially available for public/dev-store-friendly apps) and the ability to send arbitrary HTTP POSTs to the app's public webhook endpoint, both of which are within an unprivileged internet user's reach.

### Recommendation
Bind the `shop` (and ideally `topic`, `webhook-id`, `api-version`) headers into the HMAC-signable content, or otherwise cryptographically tie the claimed shop identity to the signed payload, so that a valid signature for shop A cannot be replayed as if it originated from shop B. At minimum, document/require that the signable string cover more than the raw body, and update `Request#to_signable_string` and `HmacValidator` accordingly.

### Proof of Concept
1. Install the target Shopify app on an attacker-controlled shop `attacker.myshopify.com`.
2. Trigger any webhook topic the app has registered (e.g. `orders/create`); capture the raw POST body and the `x-shopify-hmac-sha256` header sent by Shopify — this HMAC is valid because it's computed only over the body with the app's shared `api_secret_key`.
3. Replay the exact captured body and HMAC header to the app's webhook endpoint, but replace `x-shopify-shop-domain` with `victim-shop.myshopify.com`.
4. `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb`) succeeds because it only checks the raw body against the secret. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) dispatches to the handler with `shop: "victim-shop.myshopify.com"`, even though the payload/body never originated from that shop, letting the attacker inject or spoof webhook events attributed to a shop they do not control.

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
