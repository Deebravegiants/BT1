### Title
Webhook `shop` identifier is trusted for tenant routing but not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `ShopifyAPI::Utils::HmacValidator.validate` computes/compares the HMAC solely over that body. The shop identity that host applications rely on for tenant-scoped processing — `Request#shop`, sourced from the unauthenticated `X-Shopify-Shop-Domain`/`shopify-shop-domain` header — is never included in the signed bytes.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` validates a webhook exclusively via `Utils::HmacValidator.validate(request)`, which authenticates only `request.to_signable_string` (`@raw_body`): [1](#0-0) [2](#0-1) 

The `shop` field, however, is read directly from the request header, which is not part of the signed data: [3](#0-2) 

The HMAC secret (`Context.api_secret_key`) is the app's single client secret, shared across every shop that has installed the app — it is not shop-specific: [4](#0-3) 

This breaks the identity binding the host application relies on: `shop authenticated by HMAC` ≠ `shop passed to the handler as tenant key`. The verified quantity is "this body+hmac pair was signed with our app secret," while the acted-upon quantity is "this webhook belongs to shop X" — and the two are not cryptographically linked.

An attacker who has installed the app on their own store (a completely unprivileged, self-service action, not requiring any credential belonging to the victim) receives genuine, validly-signed webhook deliveries for their own shop. Because the signature covers only the body, they can replay that exact `(raw_body, hmac)` pair to the app's webhook endpoint while swapping the `X-Shopify-Shop-Domain` header to name a victim shop that also has the app installed. `HmacValidator.validate` still succeeds (body/hmac pair unchanged and valid), and `Registry.process` forwards `request.shop` — now the victim's domain — into `WebhookMetadata`, which the host application's `WebhookHandler#handle` uses to select a tenant record, session, or access token to act on: [5](#0-4) [6](#0-5) 

### Impact Explanation
Because `WebhookMetadata.shop` is the only tenant identifier the gem exposes to the handler, and it is unauthenticated, any app built on the documented `WebhookHandler` contract that uses `data.shop` to key its per-merchant state (e.g., look up stored access tokens, update records, or trigger side effects scoped to that shop) is exposed to cross-tenant confusion: attacker-controlled webhook traffic can impersonate a different shop that also installed the app. This satisfies the Critical bar of cross-tenant access, since the mismatch is rooted in the gem's own `HmacValidator`/`Request` design rather than misuse of an undocumented API.

### Likelihood Explanation
Exploitation requires only that the attacker install the target app on a shop they control (standard, self-service, unprivileged action for any public app) and be able to send arbitrary HTTP requests to the app's webhook endpoint with a modified header — no access token, `client_secret`, or victim credential is needed. This makes the attack straightforward for any user of a public/multi-tenant Shopify app built with this gem.

### Recommendation
Bind the shop identity to the signed payload before trusting it for tenant routing — e.g., include the shop domain in `to_signable_string`/HMAC computation, or independently verify `request.shop` against a per-shop record (such as a previously stored, HMAC-derived session ID) rather than trusting the raw header value. At minimum, document that `WebhookMetadata#shop` is not cryptographically authenticated and must not be used as a sole tenant key without additional verification.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the raw POST body `B` and the `X-Shopify-Hmac-Sha256` header value `H` that Shopify legitimately computed with the app's real `client_secret`.
2. Attacker replays the request to the app's webhook endpoint, keeping `body = B` and `X-Shopify-Hmac-Sha256 = H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (a shop that has also installed the app).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `B` only and matches `H` — validation passes.
4. `WebhookMetadata.new(shop: request.shop, ...)` is built with `shop = "victim-shop.myshopify.com"` and handed to the host app's `WebhookHandler#handle`, causing it to act on the victim shop's tenant context using attacker-supplied body content.

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
