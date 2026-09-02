Confirmed. This is a solid, code-provable analog: the webhook HMAC binds only the raw request body, while `shop`, `topic`, `api_version`, and `webhook_id` — read straight from unauthenticated headers — are what the library hands to the app's handler as the trusted tenant identity.

### Title
Webhook HMAC only signs the raw body, so the `shop` (tenant) identity used by `Webhooks::Registry.process` is unauthenticated and spoofable — ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies a webhook solely via `Utils::HmacValidator.validate(request)`, which computes the HMAC over `request.to_signable_string`. For `Webhooks::Request`, `to_signable_string` returns only `@raw_body` [1](#0-0) . The `shop` accessor, however, is read directly from the `x-shopify-shop-domain`/`shopify-shop-domain` header and is never included in the signed material [2](#0-1) . `Registry.process` nonetheless treats a passing HMAC check as authorizing the entire request, then forwards `request.shop` to the app's handler as the trusted tenant key [3](#0-2) , and `WebhookMetadata.shop` is documented/typed as a plain trusted `String` with no further binding [4](#0-3) .

### Finding Description
The equality that should hold is: `shop bound by HMAC == shop acted upon by the handler`. In this gem it does not — `hmac` verifies `raw_body` only [5](#0-4) , and `shop`/`topic`/`api_version`/`webhook_id` are header values consumed independently of that signature [6](#0-5) . Any party that can produce one genuine `(raw_body, hmac)` pair for the app's shared `api_secret_key` — which a malicious merchant can trivially obtain by installing the app on their own store and receiving a real webhook delivery — can resubmit that same body/HMAC pair to the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop's domain. `HmacValidator.validate` will still pass because it never looks at the shop header, and `Registry.process` will invoke the handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain [7](#0-6) . The library's own documentation reinforces the false assumption that a passing `process` call means "the request did indeed come from Shopify" for that shop [8](#0-7) , when in fact only the byte-for-byte body was verified.

### Impact Explanation
Any app built on this gem that uses `WebhookMetadata#shop` to look up per-tenant sessions/records (the exact pattern shown in the gem's own docs and tests) is exposed to cross-tenant data corruption/spoofing: an attacker-controlled shop can forge webhook deliveries that are processed as if they originated from a different, victim shop. This matches the "cross-tenant access" Critical impact category, since the tenant-identity binding the library is supposed to guarantee via HMAC verification is not actually enforced for the `shop` field.

### Likelihood Explanation
Likelihood is bounded by the attacker needing their own legitimate app installation (any developer/merchant who installs the target app can generate real signed webhook bodies for arbitrary mandatory/optional topics), then simply replaying that body+HMAC with a modified shop header to the app's public webhook endpoint. No access token, `client_secret`, or victim credentials are required — only observation of one's own webhook traffic, which is standard/expected for any app-installing merchant.

### Recommendation
Include the shop domain (and topic) as part of the signed/verified material, or independently authenticate `request.shop` against the set of shops that have valid, registered sessions/webhooks before handing it to `WebhookHandler#handle`. At minimum, the gem should document explicitly that `HmacValidator`/`Registry.process` only authenticates the body, and that `shop` must be independently cross-checked by the host application against a known-shop list before being trusted as a tenant key.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, triggering a real Shopify webhook delivery with a genuine `raw_body` and `x-shopify-hmac-sha256` signed with the app's `api_secret_key`.
2. Attacker replays this exact `raw_body`/HMAC pair to the app's webhook endpoint, replacing only the `x-shopify-shop-domain` header with `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `raw_body` only and succeeds [9](#0-8) .
4. The registered handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` [10](#0-9) , causing the host app to process attacker-controlled data under the victim tenant's identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** docs/usage/webhooks.md (L125-126)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```
