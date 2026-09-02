### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant shop spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` validates the authenticity of an incoming webhook using an HMAC computed only over the raw request body, while the `shop` (tenant identifier) is read from an unauthenticated HTTP header. This breaks the binding "shop authenticated == shop the payload is attributed to," letting an attacker who controls one legitimate webhook delivery (e.g., to their own installed shop) relabel it as belonging to a different shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not part of that signable string: [2](#0-1) 

`HmacValidator.validate` only checks `verifiable_query.to_signable_string` against the received `hmac`: [3](#0-2) 

`Registry.process` accepts the request once the body's HMAC checks out, then dispatches the handler using `request.shop` taken from the unauthenticated header, along with the (HMAC-covered) body: [4](#0-3) 

Because the same `api_secret_key` is used for every shop an app is installed on, a merchant/attacker who has the app installed on their own store receives genuine, correctly-HMAC'd webhook deliveries for their own shop. Since the signature covers only the body and not the `shop-domain` header, the attacker can replay that exact body+HMAC pair to the app's webhook endpoint while substituting the `shop-domain` header with a victim shop's domain. `HmacValidator.validate` will still succeed (it only re-hashes the raw body), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the (attacker-controlled) body belongs to the victim shop.

The equality broken is: **shop attested by HMAC ≠ shop delivered to the handler**. The gem only authenticates "this body came from Shopify with this secret"; it does not bind the body to a specific shop, so the tenant boundary is not actually enforced by this library's own verification step.

### Impact Explanation
This is a cross-tenant integrity issue: an unprivileged attacker (any merchant who can install the app on their own store) can inject or misattribute webhook events to a different, victim tenant. Host applications that key webhook handling logic off `WebhookMetadata#shop` (which is the gem's own documented mechanism for tenant dispatch) can be made to process attacker-controlled data (e.g. `orders/create`, `app/uninstalled`, `customers/data_request`, etc.) under another shop's identity, which can lead to data corruption, incorrect authorization decisions, or state changes attributed to the wrong tenant — a cross-tenant access/confusion vulnerability rooted entirely in this gem's HMAC scope.

### Likelihood Explanation
Moderate-to-high: exploitation only requires the attacker to have (or create) a shop where the target app is installed — a normal, unprivileged action available to any merchant/developer — and the ability to send arbitrary HTTP requests to the app's public webhook endpoint (which is inherently internet-facing). No access token, `client_secret`, or privileged credential is required.

### Recommendation
Bind the shop identity into the HMAC-verified material, or otherwise cryptographically/contextually tie the `shop-domain` header to the signed body (e.g., verify the shop against session/tenant records established during OAuth for that specific installation, or require the host app to independently confirm the shop belongs to an app installation before trusting `WebhookMetadata#shop`). At minimum, document prominently that `request.shop` is unauthenticated and must not be trusted for tenant isolation without additional verification.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a real event (e.g., updates an order) so Shopify delivers a genuine webhook: body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B` under the app's shared `api_secret_key`), `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker resends the identical body `B` and HMAC `H` to the same webhook endpoint, but changes only the `x-shopify-shop-domain` header to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses this successfully (`lib/shopify_api/webhooks/request.rb:45-63`), and `Utils::HmacValidator.validate` succeeds because it re-hashes only `B` (`lib/shopify_api/webhooks/request.rb:36-38`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
4. `Registry.process` invokes the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker's B>, ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing the host application to process attacker-controlled data as if it originated from the victim's store.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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
