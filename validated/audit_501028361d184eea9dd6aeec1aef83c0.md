## Title
Webhook shop identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing — (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop-domain` header — which is later trusted as the tenant identity for the webhook event — is never included in the signed bytes. `Registry.process` validates the HMAC and then unconditionally forwards `request.shop` (read straight from the unauthenticated header) to the app's handler. An attacker who can obtain one validly-signed webhook body/HMAC pair for the app (e.g. by installing the app on their own store and capturing a delivered webhook) can replay that exact body+HMAC to the app's webhook endpoint while substituting an arbitrary `shop-domain` header, and the signature check will still pass — allowing the attacker to impersonate a webhook event as if it came from a victim shop.

### Finding Description
`Request#to_signable_string` only returns the raw body: [1](#0-0) 

The `shop`, `topic`, `api_version`, and `webhook_id` accessors all read directly from HTTP headers that are not part of the signed bytes: [2](#0-1) 

`HmacValidator.validate` only checks `to_signable_string` (i.e., the body) against the secret: [3](#0-2) 

`Registry.process` validates the HMAC, then passes `request.shop` straight through to the handler as the trusted tenant identity, with no additional binding check between the signed body and the shop header: [4](#0-3) 

The broken identity binding is: `shop-domain header used as tenant identity` ≠ `shop bound by the HMAC signature`. The HMAC only proves "this body was produced using the app's shared secret" (which is the same secret across every shop that installs the app); it proves nothing about which shop the body/event belongs to. Since `shop` is not part of the signable string, any body+HMAC pair valid for one shop remains valid, byte-for-byte, when replayed with a different `shop-domain` header.

### Impact Explanation
This is a cross-tenant impersonation vector: an unprivileged user who has legitimately received one webhook for their own shop (trivial — installing the app is a normal, non-privileged action) can replay that captured body+HMAC to the app's webhook endpoint with the `shop-domain` header changed to point at a victim shop. `Registry.process` will accept it (HMAC over the body still verifies) and hand the app's handler a `WebhookMetadata` object whose `shop` field is the victim's domain but whose `body` is attacker-controlled. Depending on which topic is replayed (e.g. `app/uninstalled`, `shop/redact`, `customers/data_request`, `customers/redact`, or any custom business-logic webhook the app relies on), this can trigger destructive or sensitive actions attributed to a shop the attacker does not control — a cross-tenant access/impersonation impact.

### Likelihood Explanation
Likelihood is moderate-to-high in any deployment where the webhook endpoint is reachable over the internet without an additional shop-binding check (e.g. IP allow-listing Shopify's egress ranges), which the gem does not enforce or document as mandatory. Obtaining a valid body+HMAC pair only requires becoming a merchant of the target app (or observing/replaying a previously delivered webhook), which is an unprivileged action.

### Recommendation
Include the shop-domain (and ideally the topic/webhook-id) in the value that is authenticated, or otherwise cryptographically bind the signed body to the shop it was delivered for, before trusting `request.shop` in `Registry.process`. At minimum, document that consuming applications must independently verify that the `shop-domain` in the webhook maps to a shop with an active session/installation for this app, and must not treat the header as authenticated by the HMAC check alone.

### Proof of Concept
1. Install the target Shopify app on attacker-controlled store `attacker.myshopify.com`; capture a delivered webhook request, e.g. headers `x-shopify-topic: app/uninstalled`, `x-shopify-hmac-sha256: <valid-hmac>`, `x-shopify-shop-domain: attacker.myshopify.com`, plus the raw body.
2. Send the exact same raw body and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but change `x-shopify-shop-domain` to `victim.myshopify.com`.
3. `HmacValidator.validate` succeeds because it only checks the body: [5](#0-4) 
4. `Registry.process` forwards `shop: request.shop` (`"victim.myshopify.com"`) to the handler, which now believes this is a legitimate `app/uninstalled` (or other) event for the victim shop: [6](#0-5)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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
