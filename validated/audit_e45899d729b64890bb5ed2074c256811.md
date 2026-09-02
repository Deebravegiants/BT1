### Title
Webhook `shop` domain is not bound to the HMAC signature, allowing cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw body only, while the `shop` (tenant identity) is read from an unauthenticated header and forwarded to the app's webhook handler unchecked. This breaks the intended binding `HMAC(secret, bytes verified) == HMAC(secret, bytes the app trusts as the source-of-truth for the shop identity)`. An attacker who can obtain any one valid `(raw_body, hmac)` pair for their *own* tenant (e.g. by installing the app on a free/dev shop and capturing a webhook delivery) can replay that exact body/HMAC pair while substituting the `x-shopify-shop-domain`/`shopify-shop-domain` header with a victim shop's domain, and `Registry.process` will accept it as valid and dispatch it to the handler as if it came from the victim shop.

### Finding Description
`Webhooks::Request#hmac` is computed from the incoming `hmac-sha256` header, and `to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is derived separately from the `shop-domain` header and is never part of the signed material: [2](#0-1) 

`HmacValidator.validate` only verifies `verifiable_query.to_signable_string` (the raw body) against the HMAC, so it never checks anything about the `shop` header: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` as the tenant identity handed to the application's handler: [4](#0-3) 

This is the same class of defect as the reported issue: a value that the application *acts on* (`users.amount` / here, `shop`) is not the value that was actually *verified* (`msg.value` / here, the HMAC-covered bytes). Because Shopify apps use a single `client_secret` shared across every installing shop, any tenant that installs the app can generate a validly-signed `(body, hmac)` pair for itself, then present that same pair to the app's webhook endpoint with a different `shop-domain` header. The signature still validates because the shop header is not part of the signed content, so the forged request is dispatched to the handler carrying the victim shop's identity.

### Impact Explanation
This crosses a tenant boundary: `WebhookMetadata#shop` is the field host applications use to look up the tenant record/session and to attribute the webhook body's data. An attacker-controlled shop can therefore inject arbitrary attacker-chosen webhook payloads (subject to the constraints of whatever topic/body they can legitimately generate for their own shop) that the host application will process as belonging to a victim shop, i.e. cross-tenant access/injection using only an unprivileged app installation the attacker controls.

### Likelihood Explanation
Exploitation requires only: (1) installing the target app on any shop the attacker controls (a normal, unprivileged action available to any merchant/developer), (2) capturing one legitimate webhook delivery's raw body + HMAC header from their own shop, and (3) resending it to the app's webhook endpoint with a modified shop-domain header. No access to `api_secret_key`, access tokens, or the victim's credentials is required.

### Recommendation
Bind the shop domain (and other identity-relevant headers such as `api-version`/`webhook-id` if used for authorization decisions) into the value that is HMAC-verified, or otherwise cryptographically tie the claimed `shop-domain` header to the request — e.g., include it in `to_signable_string`, or require host applications to cross-check `request.shop` against a shop known to be entitled to the specific `webhook_id`/subscription before trusting it as a tenant key.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`) they control the body of.
2. Attacker's server logs the raw POST body and the `x-shopify-hmac-sha256` header from that genuine, validly-signed delivery.
3. Attacker replays the exact same body and HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` succeeds (HMAC only covers the body), and `Registry.process` dispatches `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker-controlled>, ...)` to the app's handler, which processes attacker-controlled data as if it came from the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-43)
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

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
