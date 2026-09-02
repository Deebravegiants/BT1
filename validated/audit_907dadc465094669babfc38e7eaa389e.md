### Title
Webhook shop/topic identity not bound to HMAC signature enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC computed over the raw request body, while the `shop`, `topic`, `api_version`, and `webhook_id` values used to route and attribute the webhook are read from unauthenticated HTTP headers. This breaks the identity binding `shop_verified_by_hmac == shop_used_by_handler`, allowing a party who possesses one validly-signed webhook body/HMAC pair to replay it with a forged `x-shopify-shop-domain` header and have the app process it under a different tenant's identity.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are all parsed straight from HTTP headers with no cryptographic binding to the signature: [2](#0-1) 

`Utils::HmacValidator.validate_signature` computes the HMAC exclusively over `verifiable_query.to_signable_string` (i.e., the raw body only) and compares it to the `hmac-sha256` header value: [3](#0-2) 

`Registry.process` treats a passing HMAC check as full authentication of the request, then forwards the unauthenticated `request.shop` (and `request.topic`) directly to the app's webhook handler as the tenant identity for the event: [4](#0-3) 

Because Shopify webhook HMACs are keyed by the app's `client_secret` (a single secret shared across every shop that installs the app, not a per-shop secret), any merchant who installs the app can legitimately receive a validly-signed webhook for their own shop. That merchant can then replay the exact same body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`) header for a victim shop. `HmacValidator.validate` still returns `true` because it only checks the body signature, and `Registry.process` will invoke the app's handler with `WebhookMetadata` claiming the victim shop as the source — `shop_verified_by_hmac (attacker's shop) != shop_trusted_by_handler (victim shop)`.

### Impact Explanation
Any downstream application logic that uses `WebhookMetadata#shop` (as passed by `Registry.process`) to key session lookups, write shop-scoped data, or trigger shop-specific side effects (e.g., updating inventory, order state, or app-installation records) can be made to act on/for a shop the attacker does not own or control, using only a webhook legitimately delivered to the attacker's own shop. This is a cross-tenant identity confusion in the gem's own webhook-processing primitive, matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires only: (1) installing the target app on an attacker-controlled shop (a normal, unprivileged action available to any merchant), (2) capturing one legitimate webhook delivery (trivial, since webhooks are sent automatically after registration), and (3) replaying the captured body/HMAC with a modified `shop-domain` header to the app's public webhook endpoint. No access token, `client_secret`, or privileged credential is required — this is fully unprivileged-internet-user reachable through the gem's documented `Registry.process` API.

### Recommendation
Include the `shop`, `topic`, and any other trust-sensitive header values in the signable string that is HMAC-verified (or otherwise cryptographically bind them to the signed payload), so that `Utils::HmacValidator.validate` fails if these fields are tampered with independently of the body. At minimum, `Webhooks::Request#to_signable_string` should incorporate the shop-domain header, and `Registry.process` should re-verify that the shop claimed in headers matches a shop actually authorized to send webhooks for the received signature.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`, obtaining a real webhook subscription.
2. Shopify delivers a legitimate webhook to the app's endpoint with body `B` and header `x-shopify-hmac-sha256: HMAC(client_secret, B)` and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker captures this request, then sends a new POST to the same endpoint with the identical body `B` and identical `x-shopify-hmac-sha256` header, but with `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which validates only over `raw_body` and returns `true` — see [5](#0-4) .
5. The handler executes with `WebhookMetadata#shop == "victim-shop.myshopify.com"`, even though the request never originated from, nor was ever authorized by, that shop.

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
