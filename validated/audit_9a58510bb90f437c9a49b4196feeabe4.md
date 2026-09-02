### Title
Webhook `shop`, `topic`, and `webhook_id` fields are trusted from unauthenticated HTTP headers while only the raw body is HMAC-verified - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, then trusts the `shop`, `topic`, and `webhook_id` values taken from HTTP headers that are never included in the signed bytes. This is structurally the same class of bug as the Astaria report: a value that is *used* by downstream trust-sensitive logic (there: `lien.amount`/slope; here: the tenant identity `shop`) is not the same value that was actually *covered* by the cryptographic check (there: `beforePayment`'s slope calc used stale, double-counted state; here: `HmacValidator` only signs `to_signable_string` = `@raw_body`).

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, and `webhook_id` are read straight from HTTP headers with no cryptographic binding to the body or to each other: [2](#0-1) 

`Registry.process` validates the HMAC (which only covers `@raw_body`) and then immediately trusts `request.shop` as the tenant identity dispatched to the handler: [3](#0-2) 

The equality the code implicitly (and incorrectly) assumes is:
`bytes_covered_by_hmac == bytes_used_to_identify_the_tenant`

but in reality:
`bytes_covered_by_hmac (raw_body) != bytes_used_to_identify_the_tenant (shop header)`

Because the app's `client_secret`/HMAC key is shared across every shop that has the app installed, any body+HMAC pair that is valid for tenant A's webhook is *also* a valid HMAC for the exact same body regardless of which shop header accompanies it — the signature says nothing about which shop the body belongs to.

### Impact Explanation
An unprivileged user who has legitimately installed the app on their own (attacker-controlled) shop can capture a real webhook delivery they receive (valid body + valid HMAC, signed with the same secret used for all shops), then replay that identical body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (or `shopify-shop-domain`) header for a victim shop. `HmacValidator.validate` will still pass (it never looked at the header), and `Registry.process` will hand the handler a `WebhookMetadata` claiming `shop: <victim>` with attacker-chosen body content. Any app that uses `data.shop` from the handler to key per-tenant storage, dispatch, or authorization decisions will process/attribute attacker data to the wrong tenant — a cross-tenant data-integrity/authorization violation, since the identity used to route the payload was never authenticated.

### Likelihood Explanation
Requires only: (1) the app be installed on any shop the attacker controls (unprivileged, self-service), and (2) the ability to send raw HTTP requests to the app's public webhook endpoint with custom headers — both are attacker-reachable without stealing credentials, without TLS interception of someone else's traffic, and without the app's `client_secret`. No privileged account or victim-side interaction is required.

### Recommendation
Bind the tenant-identifying fields into the signed payload rather than trusting bare headers: include `shop`, `topic`, and `webhook_id` in `Request#to_signable_string` (mirroring how `Oauth::AuthQuery#to_signable_string` includes `shop`), or independently verify that `request.shop` corresponds to a shop with an active, known registration/session before dispatching to the handler.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and configures a webhook so Shopify delivers a request with a known body `B` and a valid `hmac-sha256` header `H` (computed by Shopify using the app's shared secret).
2. Attacker replays this HTTP request directly to the app's webhook endpoint but changes the header from `shopify-shop-domain: attacker-shop.myshopify.com` to `shopify-shop-domain: victim-shop.myshopify.com`, keeping body `B` and hmac `H` unchanged.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `request.to_signable_string` (`B` only) and finds it matches `H` — validation succeeds. [4](#0-3) 
4. `handler.handle` is invoked with `data.shop == "victim-shop.myshopify.com"` even though the body content actually originated from the attacker's own shop, demonstrating the shop identity was never authenticated by the HMAC check. [5](#0-4)

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
