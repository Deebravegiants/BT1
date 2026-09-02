This confirms the finding: `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from unauthenticated HTTP headers [2](#0-1) . `HmacValidator.validate` only compares the HMAC over `to_signable_string` (the body) [3](#0-2) , so none of these header-derived fields are cryptographically bound to the signature. `Registry.process` then trusts `request.shop` and `request.topic` directly to dispatch to the app's handler [4](#0-3) .

### Title
Webhook `shop` and `topic` identity is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating the HMAC over the raw body [5](#0-4) , then hands the *unauthenticated* `shop`, `topic`, and `webhook_id` header values straight to the app's handler as the trusted tenant/topic identity [6](#0-5) . The signature never covers these fields, so the binding "shop that the HMAC authenticates == shop the handler is told the data belongs to" does not hold.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are parsed from headers with no cryptographic tie to the signature: [2](#0-1) 

`HmacValidator.validate` computes the signature only over that signable string (the body) and compares it to the `hmac` header value: [3](#0-2) 

Once validation passes, `Registry.process` immediately builds `WebhookMetadata` using the unauthenticated `request.shop` and `request.topic` and dispatches to the registered handler for that topic: [4](#0-3) 

Because a merchant can legitimately install the app on their own store and thus obtain at least one genuine `(raw_body, hmac)` pair signed with the app's real `client_secret` for their own shop, they can replay that exact body+HMAC pair to the app's public webhook endpoint while substituting the `shopify-shop-domain` header (and/or `shopify-topic` header) with a victim shop's domain or a different topic. `HmacValidator.validate` will still report success, because the HMAC only ever covered the body bytes, not the headers. The gem then reports this forged request to the app's handler as if it authentically originated from the victim shop/topic — breaking the equality "HMAC-authenticated body owner == shop delivered to handler."

### Impact Explanation
This is a cross-tenant identity break: an unprivileged internet user who merely holds one valid webhook body/HMAC pair for their own tenant can cause the receiving application to process/attribute that payload under another merchant's `shop` identity. Any host application that uses `WebhookMetadata#shop` (as recommended by this gem's own docs and handler interface) to select the tenant record to update will act on the wrong tenant, matching the "cross-tenant access" class of critical impact.

### Likelihood Explanation
Any user can install the app on a shop they control (no special privilege required) to obtain a valid signed webhook body for at least one topic, since Shopify will deliver real webhooks to any app the merchant installs. Headers are fully attacker-controlled at the HTTP layer reaching the app's public webhook endpoint, and the gem performs no header-level authentication—only `Utils::HmacValidator.validate(request)` on the body is checked, as shown in `Registry.process` [5](#0-4) .

### Recommendation
Extend `to_signable_string` (or `HmacValidator`) to bind the `shop`, `topic`, and `webhook_id` header values into the signature computation, or otherwise cryptographically verify these fields are consistent with Shopify's expected format/registration before passing them to `WebhookMetadata`. At minimum, document clearly that `shop`/`topic` are not covered by the HMAC so host applications do not implicitly trust them as tenant identity without additional verification (e.g., cross-checking against the caller's known/registered shop list).

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com`, triggering a real webhook, e.g. `orders/create`. They capture the raw POST body `B` and header `shopify-hmac-sha256: H`, where `H = HMAC-SHA256(client_secret, B)` [1](#0-0) .
2. Attacker sends a POST to the victim app's webhook endpoint with the same body `B` and `shopify-hmac-sha256: H`, but sets `shopify-shop-domain: victim-shop.myshopify.com` (and optionally a different `shopify-topic`).
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `HMAC(client_secret, B) == H` [7](#0-6) .
4. The handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: ..., ...)` [6](#0-5) , causing the host app to process attacker-supplied data under the victim's tenant identity.

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
