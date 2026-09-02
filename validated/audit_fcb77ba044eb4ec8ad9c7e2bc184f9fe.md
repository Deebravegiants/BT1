Confirmed: `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, and `webhook_id` are read straight from unauthenticated HTTP headers [2](#0-1) , and `HmacValidator.validate` only checks the HMAC over `to_signable_string`, i.e. the body, never the headers [3](#0-2) . `Registry.process` trusts `request.shop` verbatim once the body HMAC passes and hands it to the app's handler as the shop identity for that event [4](#0-3) .

### Title
Webhook shop-domain (and topic/webhook-id) headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`), the event type (`topic`) and the delivery id (`webhook_id`) exclusively from HTTP headers, but `to_signable_string` — the value actually protected by HMAC-SHA256 in `Utils::HmacValidator.validate` — is just the raw request body. The HMAC therefore authenticates "this body was produced with the app's `client_secret`" but says nothing about which shop, topic, or webhook the body belongs to.

### Finding Description
The intended identity binding is: `shop header used by the app == shop the HMAC actually authenticates`. In this gem that equality does not hold:

- `Request#hmac` reads `shopify-hmac-sha256` header [5](#0-4) .
- `Request#shop`, `#topic`, `#webhook_id` read the corresponding `shopify-*`/`x-shopify-*` headers, unauthenticated [2](#0-1) .
- `Request#to_signable_string` returns only `@raw_body` [1](#0-0) .
- `HmacValidator.validate_signature` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares against the received HMAC — so it only signs the body, never `shop`, `topic`, or `webhook_id` [6](#0-5) .
- `Registry.process` accepts the request as authentic once `Utils::HmacValidator.validate(request)` passes, then constructs `WebhookMetadata.new(topic: request.shop, ...)` [sic, `topic: request.topic, shop: request.shop`] straight from the unauthenticated headers and dispatches it to the app-registered handler [4](#0-3) .

Because the `client_secret` is a single per-app secret shared across every installed shop (not per-tenant), any shop that installs the app can legitimately receive a body+HMAC pair signed with that secret from one of its own real webhook deliveries. That attacker-controlled merchant can then replay the exact same body and HMAC directly to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`, `X-Shopify-Webhook-Id`) header with a victim shop's domain. `HmacValidator.validate` still returns `true` (the body and secret are unchanged), so `Registry.process` will dispatch the event to the handler tagged with the victim's shop identity, even though nothing in the cryptographic proof ties that body to that shop.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook processing: an attacker who is merely one authenticated-but-unprivileged merchant of the app can inject webhook events that are attributed to a different, victim shop. Any host application that uses `WebhookMetadata#shop` to key its per-tenant data (e.g., updating that shop's order/customer records, honoring `shop/redact` or `app/uninstalled` for a shop, or writing subscription/billing state) can be manipulated cross-tenant, since the gem provides no verification that the header-derived shop matches the body that was actually HMAC-signed. This matches the Critical bar of cross-tenant access.

### Likelihood Explanation
Exploitation only requires the attacker to control one shop that installs the app (no privileged credentials, TLS interception, or knowledge of `client_secret`/access tokens needed) and to be able to POST directly to the app's public webhook endpoint with modified headers — both are available to an ordinary unprivileged internet user/merchant.

### Recommendation
Bind the identity fields into the signed material, or otherwise cryptographically tie the header claims to the request that was verified. At minimum, `to_signable_string` (or a new binding check in `Registry.process`) should incorporate `shop`, `topic`, and `webhook_id`, or the registry should independently confirm that the shop the body claims to belong to is the shop the app actually has installed/expects for that delivery, before dispatching to handlers.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and receives a legitimate webhook, e.g. `orders/create`, with body `B` and valid header `X-Shopify-Hmac-Sha256: H` (computed by Shopify over `B` using the app's `client_secret`).
2. Attacker POSTs directly to the app's webhook endpoint with the same body `B` and the same `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `B` only [1](#0-0)  and finds it valid, since the header substitution was never part of the signed data.
4. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: ..., body: parsed(B), ...)`, causing the host app to process attacker-supplied data as if it originated from the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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
