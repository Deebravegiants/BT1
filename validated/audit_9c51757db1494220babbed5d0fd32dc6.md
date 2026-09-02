### Title
Webhook shop identity not covered by HMAC allows cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from the `X-Shopify-Shop-Domain` HTTP header, but the HMAC signature it validates against (`to_signable_string`) covers only the raw request body. The tenant-binding field an app relies on to know *which merchant* a webhook belongs to is therefore never authenticated.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from an unauthenticated header: [2](#0-1) 

`HmacValidator.validate` computes the signature only over `to_signable_string` (the body) and compares it against the `hmac` field: [3](#0-2) 

The gem exposes a `WebhookMetadata` struct with a `shop` field that host apps are expected to trust as the tenant identifier for dispatching webhook business logic: [4](#0-3) 

The identity binding that should hold is:
`HMAC-covered bytes == bytes used to determine the shop the webhook is attributed to`

In this gem that equality does not hold: `HMAC-covered bytes = raw_body` while `shop attribution = header["shopify-shop-domain"]`, a value fully controlled by whoever sends the HTTP request and never mixed into the signed payload.

### Impact Explanation
Because Shopify signs a webhook body per-shop but the header carrying the shop identity is unsigned, any party who can obtain one validly-signed webhook body (e.g., from their own store, which any developer/attacker can legitimately install the app on and receive real webhooks for) can replay that exact body to the victim app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header. `HmacValidator.validate` will still succeed because it only checks the body bytes against the HMAC, and the app will process the payload as if it came from the spoofed shop (`WebhookMetadata#shop`). Depending on the payload/topic reused (e.g., `app/uninstalled`, `shop/update`, `customers/data_request`), this allows cross-tenant confusion: data or actions attributed to shop B can be triggered using signed bytes obtained from shop A, since the identity attribute (`shop`) is not bound to the signature. This matches the Critical class of "cross-tenant access" via a broken identity binding.

### Likelihood Explanation
High: the vulnerable code path is the gem's only externally documented webhook-verification primitive (`HmacValidator.validate` + `Request#shop`), used unconditionally by any app integrating with this gem, and exploitation requires nothing more than obtaining one legitimately signed webhook body (trivially available to any developer who installs the app on a shop they control) and sending a forged HTTP request with a different shop header — no secret material is needed.

### Recommendation
Bind the shop (and other trust-relevant headers such as `topic`, `webhook-id`, `api-version`) into the signed material used for verification, or otherwise cryptographically tie the `shop-domain` header to the payload before exposing it via `WebhookMetadata`. At minimum, document/enforce that consumers must independently verify the `shop` header against their own installed-shop registry rather than trusting it as authenticated solely because `HmacValidator.validate` passed.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and receives a real webhook, e.g. `app/uninstalled`, with a valid `X-Shopify-Hmac-Sha256` header computed by Shopify over the JSON body.
2. Attacker replays the exact same body and HMAC header to the app's webhook endpoint, but changes `X-Shopify-Shop-Domain: attacker.myshopify.com` to `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` is built; `Utils::HmacValidator.validate(request)` succeeds because it only recomputes HMAC over `@raw_body`, which is unchanged. [5](#0-4) 
4. The host application, trusting the passed HMAC check, dispatches `WebhookMetadata` with `shop: "victim.myshopify.com"` to its handler, causing it to act as if the (attacker-controlled) payload came from the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
