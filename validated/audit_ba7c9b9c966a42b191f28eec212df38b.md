### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant shop-identity spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, but the tenant-identifying `x-shopify-shop-domain` header is never included in that signature. The `shop` value handed to the app's `WebhookHandler` is therefore attacker-controllable independent of the cryptographic check.

### Finding Description
`Registry.process` validates the request with `Utils::HmacValidator.validate(request)` [1](#0-0) , which computes the signature over `verifiable_query.to_signable_string`. For `Webhooks::Request`, `to_signable_string` returns only `@raw_body` [2](#0-1) . The `shop` accessor, however, is read directly and unauthenticated from the `shop-domain` header [3](#0-2) , and that same value is forwarded verbatim into `WebhookMetadata.shop`, which the app's handler uses to identify which merchant/tenant the event belongs to [1](#0-0) [4](#0-3) .

The identity binding that should hold is:
`shop_used_by_handler == shop_cryptographically_bound_by_HMAC`

In this code this equality does not hold: the HMAC only proves "the body bytes were signed with the app's `client_secret`" — a secret shared across *every* installation of the app — it proves nothing about which shop the body belongs to. Because a webhook client secret (`Context.api_secret_key`) is the same for all shops that have installed a given app, any merchant who has installed the app (an "unprivileged internet user" from the perspective of any *other* tenant) can:
1. Install the app on their own store and receive a legitimate, correctly-signed webhook (HMAC computed only over the body).
2. Replay that exact HTTP request to the app's webhook endpoint, substituting the victim's shop domain in the `x-shopify-shop-domain` header (and, for topics whose body doesn't intrinsically encode the shop, an unmodified or crafted body).
3. `HmacValidator.validate` still succeeds, because it only checks the body against the shared secret — a check that is trivially satisfiable by the attacker's own legitimately-signed payload — and `Registry.process` passes `request.shop` (now the victim's domain) straight into the handler [1](#0-0) .

Any host application that trusts `WebhookMetadata#shop` to select which tenant's data/session to act on (a documented, expected usage pattern, e.g. loading a session or performing per-shop writes keyed by `data.shop`) will process the forged event under the wrong shop's identity — a genuine cross-tenant confusion introduced by this gem's webhook verification design, since the gem exposes `shop` as if it were verified alongside the HMAC check it performs.

### Impact Explanation
This breaks the tenant boundary the HMAC check is meant to enforce: an attacker who legitimately installed the target app on any shop can produce a "validated" webhook labeled with any other shop's domain. Depending on how the host app keys work off `WebhookMetadata.shop` (e.g., looking up/activating that shop's session, writing to that shop's records, or triggering the shop's fulfilment/billing/inventory automation), this enables cross-tenant data manipulation/access — matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high for any app supporting third-party (public/multi-tenant) installs: the client secret is identical for all installs of the app, an attacker only needs their own legitimate install to obtain a validly-signed body/HMAC pair, and forging/replaying the HTTP request with a different `shop-domain` header requires no special privileges — only an HTTP client. No access token, `api_secret_key`, or leaked credential belonging to the victim is required.

### Recommendation
Bind the shop identity into the authenticated material before it is trusted:
- Include the `shop-domain` (and `topic`/`webhook-id` if used for dedup) in the HMAC-signed material, or
- Require host apps (and provide a built-in gem-level check) to cross-validate `WebhookMetadata.shop` against an actively known/registered shop for this app (e.g., an existing session store lookup) before acting on the payload, rejecting webhooks for shops that have no active installation record, and
- Document/enforce that `shop-domain` must not be treated as authenticated purely because `HmacValidator.validate` returned true.

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com`; Shopify sends a real webhook with headers `x-shopify-hmac-sha256: <valid>`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, and body `B`.
2. Attacker captures this request and replays it to the app's public webhook endpoint, unmodified except:
   `x-shopify-shop-domain: victim-shop.myshopify.com`
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` builds a request whose `to_signable_string` is still `B` [2](#0-1) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(client_secret, B)` and matches the original valid signature [5](#0-4) [6](#0-5)  — validation succeeds.
5. The registered handler receives `WebhookMetadata(shop: "victim-shop.myshopify.com", ...)` [7](#0-6) , and any host logic that keys off `data.shop` now operates as `victim-shop`, despite the event never having originated from Shopify for that shop.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```
