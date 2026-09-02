### Title
Webhook HMAC validation covers only the raw body, not the `shop-domain`/`topic`/`webhook-id` headers, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `Utils::HmacValidator.validate` verifies the HMAC exclusively against that body. The `shop-domain`, `topic`, `webhook-id`, and `api-version` values used by `ShopifyAPI::Webhooks::Registry.process` to dispatch and attribute the webhook are taken straight from HTTP headers that are **not** part of the signed content. Any entity capable of obtaining one genuinely-signed webhook body/HMAC pair for the shared app secret (e.g., by installing the public app on their own store) can replay that exact body+signature to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header, causing the handler to process the payload as though it originated from a victim shop.

### Finding Description
`HmacValidator.validate` computes `OpenSSL::HMAC.hexdigest` over `verifiable_query.to_signable_string` and compares it to the `hmac` value with `OpenSSL.secure_compare`: [1](#0-0) 

For webhooks, `to_signable_string` is defined to be just the raw body: [2](#0-1) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all pulled from HTTP headers with no cryptographic binding to the body or to each other: [3](#0-2) 

`Registry.process` validates only the HMAC (i.e., only the body) and then dispatches using the unauthenticated `request.topic` and `request.shop`: [4](#0-3) 

Because every shop that installs a given app shares the same `api_secret_key`, a signature that is valid for one shop's webhook body is also a syntactically valid signature for that same body under a different, forged `shopify-shop-domain` (and/or `shopify-topic`) header — the signature says nothing about which shop or topic the payload belongs to. An attacker only needs to be a legitimate (even free/dev) installer of the public app to harvest one valid `(raw_body, hmac)` pair, then replay it against the same endpoint with a victim shop's domain in the header. `WebhookMetadata.new(topic:, shop:, body:, ...)` is built entirely from these unauthenticated fields and handed to the app's handler, so any downstream logic that trusts `data.shop` as the tenant identifier (e.g., updating billing state, deleting shop data on `app/uninstalled`, or writing order/customer data) will act on the wrong tenant.

### Impact Explanation
This breaks the identity binding "the shop authenticated (by the shared-secret HMAC signature) versus the shop the handler stores/acts on." The HMAC is meant to authenticate that the webhook was really produced by Shopify for this app, but it never authenticates *which* shop or topic the enclosed data belongs to. This enables cross-tenant access/data injection — an attacker with a normal, unprivileged app installation on their own store can spoof events (including sensitive lifecycle events like `app/uninstalled`, `shop/redact`, or order/customer webhooks) attributed to any other merchant using the same app, without needing the app's `client_secret`, an access token, or any privileged account.

### Likelihood Explanation
Likelihood is moderate-to-high in real deployments: any user can install a public/free app on their own store to legitimately receive one signed webhook, then replay the captured body+signature against the app's public webhook endpoint with a forged shop header. No secrets, tokens, or TLS interception are required — only a normal app install and standard HTTP tooling to modify the outgoing header. The main constraint is that the replayed payload's contents are limited to whatever the attacker's own store's webhook body contained, but topic/shop values are fully attacker-controlled since they are unsigned.

### Recommendation
Include the shop domain, topic, and webhook id in the signed material (or otherwise cryptographically bind them to the request), and reject requests where the header values are not part of what was verified. At minimum, the library should document/enforce that consumers cannot trust `request.shop`/`request.topic` purely on the basis of a valid body HMAC, or the gem should incorporate these header values into `to_signable_string` so the HMAC check binds the full tuple (shop, topic, webhook_id, body) rather than just the body.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (any unprivileged party can do this for a public app) and registers/receives a real webhook, e.g. `orders/create`, with:
   - `raw_body`: some JSON payload
   - `shopify-hmac-sha256`: valid HMAC of `raw_body` computed with the shared `api_secret_key`
   - `shopify-shop-domain: attacker-shop.myshopify.com`
2. Attacker resends the exact same `raw_body` and `shopify-hmac-sha256` value to the app's public webhook endpoint, but changes the header:
   - `shopify-shop-domain: victim-shop.myshopify.com`
3. `ShopifyAPI::Webhooks::Request.new` parses these headers; `Utils::HmacValidator.validate` re-computes the HMAC over `raw_body` only, which still matches, so `Registry.process` proceeds: [5](#0-4) 
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the payload was never generated for that shop, demonstrating the cross-tenant spoof.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
