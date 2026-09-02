## Title
Webhook `shop` (and `topic`/`webhook-id`) attribution is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while the `shop`, `topic`, `webhook_id`, and `api_version` values used to route and attribute the webhook are read straight from unauthenticated HTTP headers. `Utils::HmacValidator.validate` only proves that the *body bytes* were signed with the app's `api_secret_key` — it proves nothing about which shop that body belongs to. Any party who can obtain one validly-signed `(body, hmac)` pair can replay it with an arbitrary `x-shopify-shop-domain` header and have the registry process it as if it came from a different tenant.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 

and the shop/topic/webhook-id are pulled independently from headers that are never included in the signed material: [2](#0-1) 

`HmacValidator.validate_signature` computes the HMAC solely from `verifiable_query.to_signable_string` (the raw body) and compares it against the `hmac` header: [3](#0-2) 

`Registry.process` trusts this validation and then hands the handler a `WebhookMetadata` built directly from `request.shop` (the unauthenticated header), not from anything bound to the signature: [4](#0-3) 

The identity binding that should hold is:
`shop authenticated by HMAC == shop attributed to the webhook data`

but the actual binding enforced by the code is only:
`body bytes authenticated by HMAC == body bytes parsed`

`shop` (and `topic`/`webhook_id`) sit entirely outside the HMAC's scope. Since the HMAC key (`api_secret_key`) is shared across every shop that has the app installed, anyone who can get one legitimately-signed webhook delivered to their endpoint (e.g., by installing the app on their own store/dev account) can capture that `(raw_body, hmac)` pair and replay it to the same endpoint with the `x-shopify-shop-domain` header rewritten to an arbitrary target shop. The signature still validates because it never covered the shop header, and `Registry.process` will invoke the app's handler believing the event originated from the victim shop.

### Impact Explanation
This breaks the tenant-isolation guarantee webhook consumers rely on: `Utils::HmacValidator.validate` succeeding is commonly treated by host applications as proof "this event genuinely happened on `request.shop`." An attacker who forges the shop header can make the app write, delete, or process data under an arbitrary victim shop's identity (e.g. triggering an `orders/create`-style handler with attacker-chosen body content attributed to a shop that never sent it), i.e. cross-tenant access/data corruption using only a credential the attacker legitimately owns for a *different* tenant.

### Likelihood Explanation
The attacker only needs the ability to install the target app on any shop they control (including a free Shopify development store) to receive one validly-signed webhook, then replay it against the app's webhook endpoint with a modified shop header. No access to the victim's credentials, `api_secret_key`, or access tokens is required, and no code change on the host application side is needed since it is following this gem's documented `HmacValidator`/`Registry.process` verification flow.

### Recommendation
- Include the shop domain (and ideally topic/webhook id) in the signed material verified by `HmacValidator`, or
- Require host applications to independently authenticate the shop domain (e.g. by checking it against a set of shops that have valid installations/access tokens) before trusting `WebhookMetadata#shop`, and document this requirement prominently since the gem currently implies HMAC success alone attributes the event to `request.shop`.
- At minimum, bind the header-derived identity fields into the value passed to `OpenSSL.secure_compare` so tampering with `shop`/`topic`/`webhook_id` invalidates the signature.

### Proof of Concept
1. Attacker installs the target Shopify app on their own (attacker-controlled) shop `attacker.myshopify.com`, which is legitimate and requires no privileged access.
2. Shopify delivers a real webhook to the app's endpoint with headers `x-shopify-shop-domain: attacker.myshopify.com`, a body `B`, and `x-shopify-hmac-sha256: HMAC(secret, B)`.
3. Attacker captures `(B, HMAC(secret, B))` and re-sends it to the same endpoint, changing only the header to `x-shopify-shop-domain: victim.myshopify.com`.
4. `HmacValidator.validate` recomputes `HMAC(secret, B)` from the unchanged body and it matches, so `Registry.process` calls the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)` — the app now processes attacker-controlled data attributed to the victim's shop.

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
