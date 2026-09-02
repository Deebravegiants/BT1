## Title
Webhook `shop` (and other identifying headers) are not covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
The reported Mango-protocol bug is a class of vulnerability where a value used to determine identity/entitlement (the strategy) is not bound by the check that is supposed to authenticate the request (the vault PDA discriminator check), so an attacker can substitute a different value than the one that was authorized. The same class of bug exists in this gem's webhook processing: `ShopifyAPI::Utils::HmacValidator.validate` only authenticates the **raw request body**, while the `shop` (and `topic`, `webhook_id`, `api_version`) values that the application uses to attribute the event to a tenant are read from unauthenticated HTTP headers.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from HTTP headers with no cryptographic binding to the body: [2](#0-1) 

`HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string`, i.e. the body only: [3](#0-2) 

`Registry.process` accepts the request as authentic once the body HMAC checks out, then dispatches to the handler using the unauthenticated `request.shop`, `request.topic`, and `request.webhook_id`: [4](#0-3) 

The equality that should hold is: `shop used for attribution == shop that Shopify actually signed for`. Instead, the code enforces only: `body bytes verified == body bytes parsed`, while `shop` (and topic/webhook_id) are accepted unverified. Any party who can obtain one valid `(raw_body, hmac)` pair — trivially achievable by installing the target app on their **own** shop and capturing a legitimate webhook delivery to their own endpoint — can replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header to any other shop domain. The HMAC still validates because it never covered those headers, and the handler will process the forged event as if it originated from the victim shop.

### Impact Explanation
This breaks the tenant-identity binding at the point where the app trusts webhook data to belong to a particular merchant. Depending on the host application's use of `WebhookMetadata#shop`, this enables cross-tenant data injection/corruption (e.g., an attacker triggering an `orders/create`-shaped payload attributed to a shop they don't own, or spoofing `app/uninstalled`, `shop/redact`, etc., for an arbitrary shop), which the rules classify as Critical (cross-tenant access).

### Likelihood Explanation
Exploitation only requires the attacker to control one shop that has the target app installed (any developer/merchant can do this via a free/dev store) and the ability to send an arbitrary HTTP POST to the app's public webhook endpoint — both trivially available to an unprivileged internet user, with no access token or `api_secret_key` needed.

### Recommendation
Include the identifying headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signed material, or otherwise cryptographically bind them to the body before dispatch, e.g. by computing the signature over a canonical string that concatenates headers and body, matching Shopify's guidance that the `X-Shopify-Shop-Domain` header must only be trusted after successful HMAC validation of the full payload including that header.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and registers a webhook (e.g. `orders/create`) to their own controlled endpoint.
2. Shopify delivers a legitimate webhook to the attacker's endpoint with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid hmac over raw_body>`, and some `raw_body`.
3. Attacker resends the exact same `raw_body` and `x-shopify-hmac-sha256` to the real app's `/webhook` route, but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only hashes `raw_body`; the app then invokes the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, processing attacker-controlled data as if it came from the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
