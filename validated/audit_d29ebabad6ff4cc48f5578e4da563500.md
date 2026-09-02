Confirmed: the library's own documentation states `Registry.process` "will verify the request did indeed come from Shopify" [1](#0-0)  and hands the app a `WebhookMetadata` struct whose `shop` field the docs explicitly present as trusted, verified data [2](#0-1) . But the actual HMAC signature only covers the raw body, not the `shop`, `topic`, `webhook_id`, or `api_version` header values.

### Title
Webhook shop/topic/webhook_id/api_version headers are not covered by HMAC verification, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop`, `topic`, `webhook_id`, and `api_version` are read from unauthenticated HTTP headers [3](#0-2) . `Registry.process` validates the HMAC over that signable string only, then constructs `WebhookMetadata` using the unverified `request.shop`, `request.topic`, etc. [4](#0-3) . This breaks the intended binding `hmac_signed_shop == asserted_shop`; instead the equality only holds for `hmac_signed_body == asserted_body`.

### Finding Description
`HmacValidator.validate` computes `OpenSSL::HMAC.hexdigest(sha256, api_secret_key, to_signable_string)` and compares it to the `hmac` header [5](#0-4) . For webhooks, `to_signable_string` is exactly `@raw_body` [6](#0-5) . The `shop` (and `topic`/`webhook_id`/`api_version`) accessors read directly from attacker-suppliable HTTP headers `x-shopify-shop-domain` / `shopify-shop-domain` with no cryptographic tie to the signed payload [7](#0-6) .

An unprivileged internet user who legitimately installs the target app on their own test/throwaway Shopify store can trigger any webhook topic they choose (e.g. by editing a product), capturing a genuine `(raw_body, hmac)` pair signed by Shopify with the app's real `api_secret_key`. Because the signature never covers the shop domain header, the attacker can replay that exact body+hmac to the app's webhook endpoint while substituting `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) with any victim shop domain string of their choosing. `HmacValidator.validate` still returns `true` (the body is byte-identical to what was legitimately signed), and `Registry.process` calls the handler with `WebhookMetadata.new(shop: <attacker-chosen-victim-domain>, ...)` [8](#0-7) , i.e., the equality "signed payload issuer" == "asserted shop" is broken.

### Impact Explanation
The gem's own documentation tells integrators that `Registry.process` "will verify the request did indeed come from Shopify" [1](#0-0)  and that `data.shop` is simply "The shop domain of the webhook" [9](#0-8) , without any caveat that the shop attribution is unauthenticated. An integrator following the documented usage pattern (as shown in the very same doc, `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) will process attacker-controlled data under an arbitrary victim shop's identity — enabling cross-tenant data injection/confusion (e.g., fake order/product/customer events attributed to a shop the attacker does not control). This crosses a tenant boundary using credentials the attacker legitimately possesses only for their own store, matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires only: (1) installing the target app on any shop the attacker controls (including a free development store), (2) triggering a webhook topic the app has registered, (3) replaying the captured body/HMAC to the app's public webhook endpoint with a modified `shop-domain` header. No access to the app's `api_secret_key`, no privileged account beyond a self-provisioned dev store, and no social engineering is required — this is achievable entirely by an unprivileged internet user who can install apps on their own store, which is the normal, low-barrier way to interact with a Shopify app.

### Recommendation
Include the `shop` (and ideally `topic`, `webhook_id`, `api_version`) header values in the HMAC-covered signable string, or independently verify that the asserted shop domain corresponds to a shop the app has an active, previously-established session/installation for before dispatching to the handler. At minimum, update `docs/usage/webhooks.md` to explicitly warn that `data.shop` is not cryptographically authenticated and must be cross-checked against known installed shops by the host application.

### Proof of Concept
```ruby
# 1. Attacker installs the target app on their own store "attacker-shop.myshopify.com"
#    and triggers a webhook (e.g. products/update), capturing the raw POST body and the
#    legitimate "X-Shopify-Hmac-Sha256" header Shopify sent (signed with the real api_secret_key).

raw_body = '{"id":123,"title":"pwned"}'          # captured from a real webhook to attacker's own shop
hmac_b64 = "AbCdEf...=="                          # captured X-Shopify-Hmac-Sha256, valid for raw_body

# 2. Attacker replays the exact body + hmac to the app's public webhook endpoint,
#    but swaps the shop-domain header to a victim shop they do not own/control:
POST /callback/products/update HTTP/1.1
Host: victim-app.example.com
X-Shopify-Topic: products/update
X-Shopify-Hmac-Sha256: AbCdEf...==
X-Shopify-Shop-Domain: victim-shop.myshopify.com   # attacker-controlled value, NOT covered by HMAC
X-Shopify-Webhook-Id: any-value
X-Shopify-Api-Version: 2024-01

{"id":123,"title":"pwned"}

# 3. ShopifyAPI::Webhooks::Registry.process(request) validates:
#      Utils::HmacValidator.validate(request)  # => true, since HMAC only covers raw_body
# 4. Handler is invoked with:
#      WebhookMetadata.new(topic: "products/update", shop: "victim-shop.myshopify.com", body: {...}, ...)
#    even though the payload never actually originated from victim-shop.myshopify.com.
```

### Citations

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
