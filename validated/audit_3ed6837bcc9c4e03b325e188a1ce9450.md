This confirms the docs explicitly document `Registry.process` as verifying "the request did indeed come from Shopify" based on the `shopify-hmac-sha256` header — but the HMAC only covers the raw body, and the `shop`, `topic`, `webhook_id`, `api_version` are all taken from unauthenticated headers and handed to the handler as trusted identity fields.

### Title
Cross-tenant webhook spoofing via HMAC-unbound `shop`/`topic` headers in `ShopifyAPI::Webhooks::Request` - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authentic once `Utils::HmacValidator.validate` succeeds, then forwards `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` to the app's handler as trusted tenant-identifying metadata. However, the HMAC signature only covers the raw JSON body — the `shop-domain`, `topic`, `webhook-id`, and `api-version` HTTP headers are never included in the signed content.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`, and `HmacValidator.validate_signature` computes/verifies the HMAC exclusively over that signable string: [1](#0-0) [2](#0-1) 

Meanwhile, `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` are all pulled straight from HTTP headers with no cryptographic binding to the signed body: [3](#0-2) 

`Registry.process` only checks the HMAC before dispatching to the app handler with these unauthenticated header values baked into `WebhookMetadata`: [4](#0-3) 

Because a single app's `api_secret_key` is shared across every shop that installs the app, any merchant who installs the app can trigger legitimate Shopify webhook deliveries to their own store (e.g. `orders/create`), capture the resulting `(raw_body, hmac)` pair — which is valid because it's signed with the same shared app secret — and replay that exact body/HMAC pair to the app's public webhook endpoint while substituting the `shopify-shop-domain` (and optionally `shopify-topic`, `shopify-webhook-id`) header to name a different, victim shop. `HmacValidator.validate` will still pass because it only checks the body signature, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the data belongs to the victim shop: [4](#0-3) 

The gem's own documentation states this call "will verify the request did indeed come from Shopify," which is the exact identity claim being broken — the binding `shop_header == shop_that_actually_generated(body)` is not enforced anywhere in the verification path.

### Impact Explanation
This breaks the tenant isolation the HMAC check is documented to provide. A host app that uses `data.shop` to route/queue work, look up per-shop sessions, or persist inbound data (as shown in the gem's own webhooks documentation) can be made to attribute attacker-supplied webhook content to an arbitrary victim shop, i.e., cross-tenant data injection through a self-installed instance of the same app. This matches the "cross-tenant access" Critical impact category, since it uses forged identity fields (not the attacker's real shop identity) to affect another tenant's data/processing within the app.

### Likelihood Explanation
Any user able to install the app on their own (attacker-controlled) store — an ordinary, unprivileged action requiring no special credentials, leaked secrets, or access token — can generate a validly-signed webhook body/HMAC pair and then freely re-POST it to the app's public webhook callback URL with a forged `shop-domain`/`topic` header, since nothing in `HmacValidator` or `Registry.process` binds those headers to the signed body.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the signed/verified material, or independently corroborate the `shop-domain` header against data known to the app for the given `webhook_id`/session before trusting it in `WebhookMetadata`. At minimum, document that `shop`, `topic`, `webhook_id`, and `api_version` are unauthenticated inputs that must not be trusted as tenant identity without additional verification (e.g., cross-checking against the shop that owns a currently-registered webhook subscription).

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com`; trigger an event so Shopify sends a legitimately-signed webhook (e.g. `orders/create`) to the app's registered callback, with body `B` and header `x-shopify-hmac-sha256: H` where `H = HMAC-SHA256(app_secret, B)`.
2. Capture `B` and `H` (e.g., via a proxy on the attacker's own traffic, or replaying from the attacker's own webhook logs/queue).
3. Send a new POST to the same app callback endpoint with body `B` unchanged, header `x-shopify-hmac-sha256: H` unchanged, but `x-shopify-shop-domain: victim-shop.myshopify.com` (and, if desired, a different `x-shopify-topic`).
4. `ShopifyAPI::Utils::HmacValidator.validate` returns `true` (only `B`/`H` are checked): [5](#0-4) 
5. `ShopifyAPI::Webhooks::Registry.process` invokes the registered handler with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the app to process attacker-supplied data as though it originated from the victim shop.

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
