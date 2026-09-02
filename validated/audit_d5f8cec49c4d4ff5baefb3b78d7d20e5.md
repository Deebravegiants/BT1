### Title
Webhook `shop` (and topic/webhook-id) headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `Utils::HmacValidator` verifies the HMAC solely against that body. The `shop-domain`, `topic`, `webhook-id`, and `api-version` headers — which are trusted and propagated verbatim into `WebhookMetadata` for handler dispatch — are never included in the signed material. Anyone who can obtain one valid `(body, hmac)` pair (e.g. by installing the app on their own store and capturing a webhook Shopify sends them) can replay that exact body/hmac pair to the app's webhook endpoint while substituting an arbitrary `shop-domain` header, and the library will accept it as a validly-signed webhook "from" that arbitrary shop.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` performs a single authenticity check: [1](#0-0) 

The only thing validated is `Utils::HmacValidator.validate(request)`, which computes the signature over `request.to_signable_string`: [2](#0-1) 

That method returns only `@raw_body`:
```ruby
def to_signable_string
  @raw_body
end
```

Meanwhile `request.shop`, `request.topic`, and `request.webhook_id` are read straight from HTTP headers with no cryptographic binding to the signed payload: [3](#0-2) 

And `HmacValidator` only checks the HMAC over that signable string using `OpenSSL.secure_compare`: [4](#0-3) 

Because the shop identity is not part of the signed data, the equality the system implicitly relies on — "the shop whose secret produced this HMAC" == "the shop named in the `shop-domain` header" — does not actually hold. `HmacValidator.validate` only proves "this body was signed with the app's secret at some point, for some shop event"; it says nothing about which shop the header claims. `Registry.process` then trusts the header value directly when building `WebhookMetadata`: [5](#0-4) 

An attacker who is a legitimate (but low-privilege) merchant/installer of the app can trigger a real webhook for their own shop, capture the resulting `(raw_body, x-shopify-hmac-sha256)` pair from the wire, and then send a forged HTTP request to the app's public webhook endpoint reusing that same body/hmac while setting `x-shopify-shop-domain` to a victim shop's domain (and/or a different `topic`/`webhook-id`). `HmacValidator.validate` will still pass, because the signature only covers the body, and the handler will be invoked with `data.shop` equal to the attacker-chosen victim domain.

### Impact Explanation
This breaks the shop/tenant identity binding that host applications rely on to decide which merchant's data or session to act upon (`data.shop` in `WebhookMetadata`). Depending on how a host app implements its webhook handlers (a documented, intended use of this API per `docs/usage/webhooks.md`), this can be leveraged to inject or spoof events attributed to a shop the attacker does not control — e.g. faking an `app/uninstalled`, `shop/update`, or order/customer webhook for a victim tenant, causing the host app to mutate or expose data tied to the victim's session/tenant record. This is a cross-tenant identity-confusion vulnerability rooted entirely in this gem's signature-verification logic.

### Likelihood Explanation
Medium: exploitation requires the attacker to obtain at least one legitimately signed `(body, hmac)` pair, which is easy to do because any user can install the app on their own free/dev shop and trigger webhook deliveries to observe body/hmac pairs (webhook bodies for many topics are attacker-influenced, e.g. `shop/update`, `carts/create`-style payloads, or even a minimal empty body). No access to `api_secret_key` or any privileged credential is needed — only the ability to author or observe one webhook delivery.

### Recommendation
Bind the identity fields into the signed material, or otherwise cryptographically verify them, before trusting them:
- Prefer validating `shop-domain` (and `topic`/`webhook-id`) against the shop cataloged in the app's own session/install store rather than trusting the header verbatim.
- If Shopify's wire format cannot be changed (since Shopify itself signs only the body), the library should clearly document that `request.shop`/`request.topic` are **not** authenticated by `HmacValidator.validate`, and require callers to cross-check `request.shop` against a known/installed shop list before dispatching, rather than allowing `Registry.process` to hand an unauthenticated shop value directly to handlers as though it were verified.

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com` and configures a webhook subscription for a topic with a predictable/empty body (or observes one delivered by Shopify).
2. Attacker captures the raw POST body and its `X-Shopify-Hmac-Sha256` header from that legitimate delivery.
3. Attacker sends a new POST to the same app webhook endpoint with:
   - the identical raw body and `X-Shopify-Hmac-Sha256` value,
   - `X-Shopify-Topic` and `X-Shopify-Shop-Domain` set to a victim's values (e.g. `victim-shop.myshopify.com`).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `raw_body` against the secret — it never inspects `shop-domain`.
5. The registered handler executes with `WebhookMetadata#shop == "victim-shop.myshopify.com"`, even though the payload actually originated from the attacker's own shop event.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
