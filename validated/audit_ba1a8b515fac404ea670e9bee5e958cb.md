### Title
Webhook shop/topic/id headers trusted but not covered by HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then trusts the `shop`, `topic`, `webhook_id`, and `api_version` values taken from unauthenticated HTTP headers to route and label the payload. Because these header values are never included in the signed content, an attacker who possesses any one valid `(raw_body, hmac)` pair signed with the app's shared `client_secret` can re-send that same body with a forged `shop-domain` (or `topic`) header and have it accepted and processed by the app as belonging to a different tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are read straight from HTTP headers and are not part of the signed material: [2](#0-1) 

`Registry.process` validates only the HMAC (which covers the body) and then immediately trusts `request.shop`/`request.topic` to build the `WebhookMetadata` handed to the app's handler: [3](#0-2) 

`HmacValidator.validate` computes the signature only over `verifiable_query.to_signable_string` (the raw body, in this case) using the app's single, shop-independent `api_secret_key`: [4](#0-3) 

The identity binding that should hold is:
`shop_authenticated_by_hmac == shop_used_by_handler_for_tenant_routing`

In this code, the left side does not exist at all — the HMAC authenticates only the body bytes, not the shop/topic/id headers — so the equality is never enforced. Since a single app-level `client_secret` signs webhooks for *every* merchant shop that installs the app, any unprivileged user who installs the public app on their own (free/dev) store legitimately receives a correctly-signed `(raw_body, hmac)` pair. That header/body pair can then be replayed directly to the app's public webhook endpoint with the `x-shopify-shop-domain` (or `shopify-shop-domain`) header rewritten to a victim shop's domain (and/or the topic changed), and `Utils::HmacValidator.validate` will still return `true` because it only checks the untouched body bytes.

### Impact Explanation
This breaks the shop-tenant isolation boundary the HMAC check is supposed to enforce: `WebhookMetadata.shop`, delivered to the app's `WebhookHandler#handle`, can be spoofed to any shop domain string chosen by the attacker while still passing signature validation. Depending on how the host application uses `data.shop` (e.g., as a lookup key to a merchant's stored session/access token, or as the tenant identifier for writing/reading merchant data), this enables cross-tenant data confusion/injection — an attacker-controlled webhook body can be processed under a victim shop's identity, or with a spoofed `topic` triggering unintended handler logic. This falls under the "cross-tenant access" high-impact category from the given rules.

### Likelihood Explanation
Reachable by an unprivileged internet user: no `api_secret_key`, access token, or privileged account is required — only (1) the ability to install the app on any shop (including a free/dev store) to legitimately capture one valid `(raw_body, hmac)` pair, and (2) the ability to send arbitrary HTTP requests to the app's public webhook endpoint with attacker-chosen headers. Both are standard, unprivileged capabilities.

### Recommendation
Bind the shop/topic/webhook identity to the signature: include `shop`, `topic`, and `webhook_id` in the signable string used for HMAC computation (or otherwise cryptographically bind them, e.g. HMAC over `header-values + body` instead of body alone), so that a signature is only valid for the exact tuple of `(shop, topic, id, body)` it was issued for, not for the body in isolation.

### Proof of Concept
1. Attacker installs the target public app on their own store `attacker-shop.myshopify.com`.
2. Shopify sends a genuine webhook to the app's endpoint with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <valid-hmac-of-body>` and some JSON body `B`.
3. Attacker captures `(B, valid-hmac-of-B)`.
4. Attacker sends a new POST directly to the app's public webhook endpoint reusing body `B` and its valid HMAC, but with `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `B`'s signature (line 190 in `registry.rb`, line 12 in `hmac_validator.rb`).
6. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: "orders/create", body: B, ...)`, i.e., attacker-controlled body is processed under the victim shop's identity. [3](#0-2) [1](#0-0)

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
