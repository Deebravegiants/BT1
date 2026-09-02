### Title
Webhook HMAC does not bind `shop-domain` or `topic` headers, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC verified by `Utils::HmacValidator.validate` never covers the `shop-domain` or `topic` headers. `Registry.process` nonetheless trusts `request.shop` and `request.topic` (both read straight from unauthenticated headers) to route the payload to a handler and to identify the tenant, breaking the intended binding: `HMAC-covered bytes == bytes acted on for tenant/topic identity`.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 

only the `@raw_body` is signed. The `shop` and `topic` accessors read directly from HTTP headers with no cryptographic binding to the HMAC: [2](#0-1) 

`Utils::HmacValidator.validate` checks only `verifiable_query.hmac` against `verifiable_query.to_signable_string` (i.e., the body): [3](#0-2) 

`Registry.process` validates the HMAC and then dispatches based on the unauthenticated `request.topic`, forwarding the unauthenticated `request.shop` straight into `WebhookMetadata`, which host applications use as the tenant identifier for persisting/acting on the payload: [4](#0-3) 

Because `shop-domain` and `topic` are not part of the signed content, and the HMAC secret (`api_secret_key`) is shared across all shops for a given app (not shop-specific), a valid `(body, hmac)` pair captured from one legitimately-delivered webhook can be replayed to the app's public webhook endpoint with a forged `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header and will still pass `HmacValidator.validate`. This equality is broken:
`shop authenticated by HMAC` != `shop stored/acted on by the handler (request.shop)`.

### Impact Explanation
An attacker who has legitimately received at least one real webhook delivery (e.g., by installing the target app on their own store, which is available to any unprivileged user for public apps) obtains a valid `(raw_body, hmac)` pair. They can then send that exact body+hmac to the app's shared webhook endpoint while substituting an arbitrary victim `shop-domain` header. Since the gem's own signature check never covers that header, `Registry.process` accepts the request as authentic and passes the attacker-chosen `shop` value to the application's webhook handler. Any host application that uses `data.shop` (per `WebhookMetadata`) to select which tenant's records to update will write or act on the attacker-controlled payload under an arbitrary shop identity — a cross-tenant data confusion/injection scenario, matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Any internet-facing app using this gem's webhook registry exposes a single, unauthenticated-by-header endpoint. Obtaining one valid `(body, hmac)` pair requires no privileged credentials — only a free/trial install of the target app, which is standard for the Shopify app ecosystem. Replaying the request with a forged shop header is trivial (a raw HTTP POST). Likelihood is therefore realistic for any consumer relying on `WebhookMetadata#shop` for tenant scoping, though actual exploitability also depends on host-application logic trusting `data.shop` without additional server-side shop verification (e.g., cross-checking against an actively registered/installed shop list).

### Recommendation
Include `shop`, `topic`, and `webhook_id` (or otherwise cryptographically bind the headers) in the value verified against the HMAC, or explicitly document that `request.shop`/`request.topic` are unauthenticated and that host applications MUST independently verify the shop domain (e.g., against a list of currently-installed/active shops) before acting on webhook data. At minimum, `Registry.process` should not silently pass an unauthenticated `shop` value into `WebhookMetadata` without a documented warning of this trust boundary.

### Proof of Concept
1. Attacker installs the target Shopify app on their own dev/trial store and registers a webhook (e.g., `orders/create`) pointing to a server they control, or sniffs any webhook delivery reaching the app's public endpoint for their own shop.
2. Attacker captures the raw JSON body and the `X-Shopify-Hmac-Sha256` header from that legitimate delivery.
3. Attacker sends a POST directly to the app's shared webhook endpoint with the same body and HMAC header, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and optionally a different `X-Shopify-Topic`).
4. `Utils::HmacValidator.validate` succeeds because it only re-hashes `@raw_body` [1](#0-0) ; `Registry.process` proceeds and calls the registered handler with `shop: "victim-shop.myshopify.com"` [4](#0-3) , causing the host app to process attacker-controlled data under the victim's tenant identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
