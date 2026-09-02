### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` that a webhook is attributed to purely from the `x-shopify-shop-domain` HTTP header, while the HMAC signature that `Webhooks::Registry.process` verifies is computed only over the raw request body. Because the app's `api_secret_key` is shared across every shop that installs the app, a valid `(body, hmac)` pair captured from one tenant's webhook can be replayed against another tenant's data path simply by swapping the `shop-domain` header, since that header is never part of the signed content.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from an unauthenticated header, independent of the signed payload: [2](#0-1) 

`HmacValidator.validate` only checks `verifiable_query.hmac` against `verifiable_query.to_signable_string`: [3](#0-2) 

`Registry.process` verifies the HMAC and then immediately trusts `request.shop` (and `request.topic`) to dispatch the handler, with no secondary check binding the shop header to the signed body: [4](#0-3) 

The binding that is broken is:

`shop authenticated by the request == shop the HMAC signature was actually computed for`

Before the attack: for a genuine webhook, the header `shop-domain` happens to equal the shop that Shopify generated the body/HMAC for, but this equality is coincidental — nothing in the code enforces it. After the attack: an unprivileged user who controls one shop that installed the app can capture a legitimate `(raw_body, hmac)` pair from their own shop's webhook (since the app's `api_secret_key` is identical for all installs of the app) and resend it to the app's webhook endpoint with `x-shopify-shop-domain` changed to a victim shop. `HmacValidator.validate` still passes because it only checks the body's HMAC, and `Registry.process` hands the handler a `WebhookMetadata` claiming the victim shop, with attacker-controlled body content.

This mirrors the report's bug class: a value used for a security/identity decision (the price's freshness / the request's tenant) is not actually covered/verified by the mechanism relied upon to prove authenticity (the heartbeat / the HMAC), so stale or attacker-controlled data is trusted as if it were verified.

### Impact Explanation
If the host application uses `WebhookMetadata#shop` to key per-tenant state (create/update records, trigger actions, index by shop domain, etc.) — which is the documented purpose of the field per `handler.handle(data: WebhookMetadata.new(topic: ..., shop: request.shop, ...))` — an attacker who is a legitimate low-privilege user on their own store can cause data to be written or actions to be executed as if they belonged to a completely different, victim merchant. This is a cross-tenant access impact (Critical), achieved without possessing the victim's access token, `client_secret`, or session — only the shared app secret's ability to validate the attacker's own genuine webhook body.

### Likelihood Explanation
Any developer or app owner who installs the app on their own store already possesses a full set of legitimate `(raw_body, hmac)` pairs from their own webhooks (visible in their own server logs/inbound requests) and controls the outgoing header values when replaying the request to the target app endpoint. No secrets need to be stolen; the shared `api_secret_key` behavior of Shopify apps is standard, and the header is fully attacker-controlled during replay.

### Recommendation
Bind the shop identity into what is cryptographically verified, or otherwise cross-check it against Shopify-controlled data rather than trusting a raw header value in isolation:
- Confirm the `shop-domain` header against an out-of-band, already-authenticated source (e.g., only accept it if a corresponding session/webhook registration for that shop+topic exists and was registered by this app instance), and/or
- Require callers of `Registry.process` to supply the expected shop (from their own trusted routing/session context) and reject processing when it disagrees with `request.shop`, and/or
- Document explicitly (and enforce where possible) that `WebhookMetadata#shop` is not itself authenticated by the HMAC and must not be used as the sole tenant-scoping key without additional verification.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a normal, unprivileged install).
2. Attacker triggers a webhook event on their own shop and captures the raw POST: `raw_body`, `x-shopify-hmac-sha256`, `x-shopify-topic`, `x-shopify-webhook-id`, `x-shopify-api-version`.
3. Attacker resends the identical request to the app's webhook endpoint, changing only `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `raw_body` only — it matches, since the body and secret are unchanged: [5](#0-4) 
5. The handler executes with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: attacker_controlled_body, ...)`, and any host-app logic keyed on `shop` now operates on the victim's tenant using attacker-supplied data.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
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
