## Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

## Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from only the raw request body, while the `shop` (and `topic`/`webhook_id`) values used to route and label the webhook data are read straight from unauthenticated HTTP headers. Because a single app's `api_secret_key` is shared across every shop that installs it, any tenant that receives one genuine, Shopify-signed webhook for their own store can replay that exact `(raw_body, hmac)` pair while substituting the `shop-domain` header for a different, victim tenant. `Registry.process` still reports `Utils::HmacValidator.validate` as successful and forwards the attacker-chosen body labeled as coming from the victim shop.

## Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` (and `topic`, `webhook_id`) are read directly from headers with no cryptographic binding to the signature: [2](#0-1) 

`Registry.process` validates only the HMAC computed over that signable string, then immediately trusts `request.shop` (and other unsigned headers) to build the data delivered to the handler: [3](#0-2) 

`HmacValidator.validate` verifies the HMAC exactly as constructed above, over `verifiable_query.to_signable_string` (i.e., body only): [4](#0-3) 

The identity binding that should hold is:
`HMAC_valid(raw_body, shop_header) == true` implies the webhook truly originates from `shop_header`.

What is actually checked is only:
`HMAC_valid(raw_body) == true`,

with `shop_header` accepted unauthenticated. Since the HMAC secret (`api_secret_key`/`client_secret`) is identical for every shop that has the app installed, any shop that has installed the app can obtain a legitimately Shopify-signed `(raw_body, hmac)` pair for its own tenant, then replay it to the app's webhook endpoint with the `x-shopify-shop-domain` (or `shopify-shop-domain`) header swapped to a different, victim shop's domain. `HmacValidator.validate` still returns `true` because it never examines the shop header, and the handler receives `WebhookMetadata` attributing the attacker-controlled body to the victim shop.

This is the direct analog of the reported bug class: `executeTransaction` checked only a subset of identifiers (transfer/approve) while leaving other, semantically-equivalent fields (`increaseApproval`) unchecked, allowing the daily-limit binding to be bypassed. Here, the webhook processor checks only the body's HMAC while leaving the semantically load-bearing `shop` identifier completely outside the signed payload, allowing the shop-binding to be bypassed.

## Impact Explanation
This breaks tenant isolation for any host application that dispatches or stores data keyed by `WebhookMetadata#shop` (e.g., looking up a merchant's session/access token by shop, updating merchant-specific records, or triggering merchant-scoped side effects such as `app/uninstalled` cleanup). An attacker who controls one legitimate installation of the app can inject arbitrary attacker-chosen webhook payloads that the app will treat as authentic events for any other merchant/shop, since the shop identity is never included in the cryptographic check. This is a cross-tenant integrity/isolation violation stemming directly from this gem's webhook verification logic.

## Likelihood Explanation
Any unprivileged actor can install a public/free instance of the target app on their own store to legitimately receive Shopify-signed webhooks (any topic works, since the body is unrestricted content payloads such as JSON). Capturing a raw body plus its HMAC header requires no privileged credentials, secrets, or social engineering — only observing traffic to their own webhook endpoint (e.g., via a proxy they control) or triggering an event on their own store. Replaying the same bytes with a modified shop header is a trivial HTTP replay.

## Recommendation
Include the shop domain (and ideally topic/webhook id/api version) in the HMAC-signed content, or otherwise cryptographically bind them to the request before trusting `request.shop`, e.g. by having `to_signable_string` incorporate the shop header, or by requiring apps to independently verify that `request.shop` corresponds to an app installation they expect before processing. At minimum, document and enforce that `Registry.process` must not be relied upon to authenticate the shop identity, and provide a dedicated verified accessor for shop that fails if it cannot be bound to the signed payload.

## Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`.
2. Shopify sends a genuine webhook to the app's endpoint:
   - Headers: `x-shopify-hmac-sha256: <valid HMAC of body>`, `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-topic: orders/create`
   - Body: attacker crafts the store's own order data at will (attacker controls their own store's order content).
3. Attacker captures `(raw_body, hmac)` and resends the exact same request to the app's webhook endpoint, only changing the header to `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request#hmac` and `#to_signable_string` are unaffected by the header swap (`to_signable_string` returns only `@raw_body`), so `Utils::HmacValidator.validate` returns `true`.
5. `ShopifyAPI::Webhooks::Registry.process` invokes the registered handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker JSON>, ...)`, causing the host app to process attacker-controlled content attributed to a shop the attacker does not own or control.

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
