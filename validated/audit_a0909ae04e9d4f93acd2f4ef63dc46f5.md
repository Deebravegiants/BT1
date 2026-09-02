### Title
Webhook `shop` (and `topic`/`api_version`/`webhook_id`) headers are trusted for tenant identity without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while `ShopifyAPI::Webhooks::Registry.process` uses the unauthenticated `shop-domain` header to build the `WebhookMetadata` passed to the app's handler. The HMAC that `Utils::HmacValidator.validate` checks therefore only binds the *body bytes* to the shared secret; it says nothing about which shop the request claims to be from. Any actor who can obtain one validly-signed webhook body (e.g. for a shop they themselves own, or a mandatory/public topic payload) can resend it with an arbitrary `x-shopify-shop-domain` header value and the signature check still passes.

### Finding Description
- `Request#to_signable_string` is defined as `@raw_body` only: [1](#0-0) 
- `Request#shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no relation to the signed payload: [2](#0-1) 
- `HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` (i.e., only the body) and compares it against the `hmac` header, never touching `shop`, `topic`, `api_version`, or `webhook_id`: [3](#0-2) 
- `Registry.process` accepts the request once the body HMAC checks out, then forwards the unauthenticated `request.shop` (plus `topic`, `api_version`, `webhook_id`) straight to the registered handler via `WebhookMetadata`: [4](#0-3) 
- `WebhookMetadata.shop` is a plain `String` const with no additional verification, and it is the field host applications are expected to use to scope the incoming webhook to a tenant: [5](#0-4) 

The broken identity binding: `HMAC-verified bytes (raw_body)` ≠ `bytes trusted for tenant identification (shop-domain header)`. A valid HMAC only proves "this body was signed with `api_secret_key`" — it never proves "this body/shop pairing was signed with `api_secret_key`". Because headers ride outside the signature, an attacker who owns a shop that legitimately receives Shopify webhooks (or who has access to any correctly-signed webhook body, including for mandatory topics like `customers/data_request`) can replay that exact body with a modified `shop-domain` header pointing at a different shop, and `Registry.process` will hand the handler a `WebhookMetadata` claiming to be from the victim shop.

### Impact Explanation
This is a cross-tenant identity confusion inside the gem's own webhook-processing path: the library asserts message authenticity via HMAC but silently allows the `shop` field consumed by the handler to be attacker-controlled. Any host application that relies on `WebhookMetadata#shop` (as documented) to route data updates, credential lookups, or session loads per-tenant can be made to act on/for the wrong shop using a replayed-but-relabeled payload, meeting the "cross-tenant access" bar.

### Likelihood Explanation
Exploitation requires the attacker to possess at least one validly HMAC-signed webhook body — achievable by any developer/store owner who has their own Shopify app installation (a normal, unprivileged capability) and can capture their own shop's outbound webhook traffic, or by using a mandatory webhook payload structure. No `api_secret_key`, access token, or privileged account is needed; the attacker only needs to control the HTTP request headers sent to the app's own webhook endpoint, which is standard unauthenticated internet-request tampering.

### Recommendation
Include the shop domain (and ideally topic/api_version/webhook_id) in the signable content that is verified against the HMAC, or otherwise cryptographically bind these header values to the signed body before exposing them via `WebhookMetadata`. At minimum, `ShopifyAPI::Webhooks::Registry.process` should cross-check `request.shop` against an independently trusted source (e.g., the shop associated with the session/registration) rather than trusting the raw header value.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` (or any shop under their control) and lets Shopify deliver a legitimate webhook, e.g. for `customers/data_request`, capturing the exact `raw_body` and its correctly computed `x-shopify-hmac-sha256`.
2. Attacker resends this exact body/HMAC pair to the app's webhook endpoint but replaces the `x-shopify-shop-domain` header with `victim-shop.myshopify.com`.
3. `HmacValidator.validate` recomputes the signature over `to_signable_string` (`@raw_body` only) using `Context.api_secret_key`; since the body is unchanged, the signature matches: [6](#0-5) 
4. `Registry.process` proceeds and invokes the registered handler with `WebhookMetadata.new(... shop: request.shop ...)`, where `request.shop` now equals `victim-shop.myshopify.com`, even though the payload was never signed by/for that shop: [7](#0-6) 
5. Any host application logic keyed off `data.shop` (e.g., "delete/return customer data for this shop") now operates against the victim shop using attacker-supplied, HMAC-unverified tenant identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L13-22)
```ruby
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
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
