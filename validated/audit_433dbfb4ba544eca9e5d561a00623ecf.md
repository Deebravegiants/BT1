Based on my research, I found a concrete analog to the reported bug class.

### Title
Webhook `shop` (and `topic`/`api_version`/`webhook_id`) identity fields are not covered by the HMAC, allowing shop impersonation - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC computed over the raw request body. The `shop` (and `topic`) that get passed to the app's webhook handler are read from HTTP headers that are never included in that signed payload. Any actor who can obtain one valid `(raw_body, hmac)` pair for the app (e.g. by owning a legitimate, low-privilege installation of the app on their own store, which is enough to receive real webhooks) can replay that body/hmac combination while forging the `shop-domain` header to any other shop, and the app will process it as authentic data for the victim shop.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all pulled straight from unauthenticated HTTP headers: [2](#0-1) 

`Registry.process` verifies only the HMAC over the body, then immediately trusts `request.shop`/`request.topic` to build the `WebhookMetadata` handed to the app's handler: [3](#0-2) 

`HmacValidator.validate` confirms only that the *body* was signed with the app's secret — it says nothing about which shop or topic the signature was meant for: [4](#0-3) 

The broken identity binding, stated as an equality that the code assumes but never checks:
`hmac_signature == HMAC(raw_body)` is verified, but the code treats this as if `shop_header == shop_that_actually_produced(raw_body)` — an equality that is never enforced. `shop`, `topic`, `api_version`, and `webhook_id` are headers, not part of the signed payload, so nothing binds them to the signature.

### Impact Explanation
Any merchant who installs the app on their own store (an unprivileged, low-cost action — no admin access token or client_secret required) can capture one legitimate `(raw_body, hmac)` pair delivered to their own webhook endpoint (e.g. by triggering an `orders/create` or `app/uninstalled` event on their own store). They can then POST that exact body+hmac to the app's public webhook endpoint while setting `X-Shopify-Shop-Domain` (and optionally `X-Shopify-Topic`) to a victim shop's domain. Since `Registry.process` never checks that the signed body actually corresponds to the claimed shop/topic, the app's handler will execute victim-shop logic (e.g. deleting the victim's stored session/data on a forged `app/uninstalled`, or injecting attacker-controlled order/customer data attributed to the victim's tenant) — a cross-tenant data-integrity/impersonation vulnerability.

### Likelihood Explanation
Low difficulty: the attacker needs no secrets beyond installing the app themselves (a normal user action), can generate arbitrary valid `(body, hmac)` pairs by triggering webhooks on their own shop, and only has to forge a plain HTTP header to redirect the payload to any other tenant. This mirrors the reported bug class exactly ("a field acted on but not covered by the HMAC").

### Recommendation
Include the shop domain, topic, webhook id, and API version in the HMAC-signed payload (or otherwise cryptographically bind them to the signature) so that `Registry.process` can verify that the values used to route/attribute the webhook are the same ones that were actually signed, not just headers copied verbatim from the request.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives a legitimate webhook, e.g.:
```
POST /webhooks HTTP/1.1
X-Shopify-Topic: app/uninstalled
X-Shopify-Hmac-Sha256: <valid-hmac-of-body>
X-Shopify-Shop-Domain: attacker-shop.myshopify.com
X-Shopify-Webhook-Id: ...

{}
```
2. Attacker replays the identical body and `X-Shopify-Hmac-Sha256` value to the same endpoint, but changes the header:
```
X-Shopify-Shop-Domain: victim-shop.myshopify.com
```
3. `Utils::HmacValidator.validate` in [5](#0-4)  still passes because it only checks the body's HMAC. `Registry.process` then invokes the app's handler with `shop: "victim-shop.myshopify.com"`, causing the app to perform victim-shop-scoped actions (e.g. purge victim session data on a forged `app/uninstalled` webhook) triggered entirely by the attacker.

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
