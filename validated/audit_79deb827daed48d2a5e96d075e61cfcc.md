### Title
Webhook `shop` domain is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body. The `shop` (and `topic`/`webhook_id`) values that the handler subsequently trusts to attribute the payload to a specific merchant are read from HTTP headers that are **not included** in the signed material. This breaks the identity binding `HMAC-verified bytes == bytes used to attribute the event to a shop`, letting any internet user who can obtain one valid `(body, hmac)` pair for the app (e.g. by installing the app themselves and triggering a webhook on their own store) replay that exact body with a forged `x-shopify-shop-domain` header pointing at any other shop that has the app installed.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are parsed straight from headers with no cryptographic binding to the signature: [2](#0-1) 

`Registry.process` validates only the HMAC over the body, then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` to build the `WebhookMetadata` handed to the app's handler: [3](#0-2) 

The security-relevant equality the gem should be enforcing is:
`shop bound to the verified signature == shop the handler acts on`

Instead the check only proves `hmac == HMAC(body, client_secret)`; it says nothing about which shop, topic, or webhook id that body is attributed to. Any request with a body/hmac pair valid for the app (obtainable by any account that can install the app — e.g. via the free developer/trial-store install flow that public Shopify apps allow) can be replayed with an arbitrary `x-shopify-shop-domain` value, because the header is never part of the signable string.

### Impact Explanation
This is a cross-tenant access vector: the webhook endpoint is the host application's own internet-facing route, secured only by this gem's `HmacValidator`/`Registry.process`. An attacker who installs the target app on a shop they control can:
1. Trigger any webhook topic (e.g. `orders/create`, `app/uninstalled`, `customers/data_request`) with content they fully control (order fields, customer fields, etc.), obtaining a legitimate `(raw_body, x-shopify-hmac-sha256)` pair signed with the app's shared `client_secret`.
2. Replay that exact body and HMAC to the app's webhook endpoint, only changing the `x-shopify-shop-domain` (and optionally `x-shopify-topic`) header to name a different, victim shop that also has the app installed.
3. `Registry.process` validates the (unchanged) HMAC successfully and dispatches `WebhookMetadata` carrying the attacker-chosen `shop` value straight to the app's business logic.

Because host applications built on this gem are expected to key their data/actions off `WebhookMetadata#shop` (per the gem's own documented `WebhookMetadata` contract), this allows an unprivileged attacker to inject fabricated events attributed to any other tenant of the app, without ever obtaining that tenant's access token or the app's `client_secret` — satisfying the "cross-tenant access" criterion.

### Likelihood Explanation
The primitive requires only that the attacker be able to install the target app on a shop they control (true for any public Shopify app, which anyone can install on a free development store) and be able to send arbitrary HTTP requests to the app's public webhook endpoint — both are unprivileged-internet-user actions with no credential leakage or social engineering needed.

### Recommendation
Bind the shop (and ideally topic/webhook id) to the verified signature instead of trusting unauthenticated headers:
- Compute/verify HMAC over a canonical string that includes `shop`, `topic`, and `webhook_id` concatenated with the raw body (this requires a corresponding change on how Shopify signs webhooks, so at minimum the gem should require the host app to cross-check `request.shop` against the shop of the session/store the app expects for that endpoint), or
- Explicitly document and enforce that `Registry.process` callers must independently authenticate the shop association (e.g. verify the shop exists in app's own session store as an installed tenant) before trusting `data.shop`, and reject requests whose `shop` header does not correspond to a known, installed tenant prior to invoking the handler.

### Proof of Concept
```ruby
# Step 1: Attacker installs the target app on their own shop "attacker.myshopify.com"
# and triggers e.g. `customers/update` with a body they fully control, capturing:
raw_body = '{"id":1,"email":"victim-data@attacker.com"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)
hmac_b64 = Base64.encode64(hmac)   # this is a legitimately Shopify-signed HMAC for raw_body

# Step 2: Attacker replays the same body+hmac to the app's public webhook endpoint,
# but swaps the shop-domain header to the victim shop.
forged_headers = {
  "x-shopify-topic" => "customers/update",
  "x-shopify-hmac-sha256" => hmac_b64,
  "x-shopify-shop-domain" => "victim-shop.myshopify.com",   # <- unauthenticated, attacker-controlled
  "x-shopify-webhook-id" => "attacker-chosen-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

# Step 3: HMAC validation passes because it only checks raw_body against the shared secret;
# it never checks that "victim-shop.myshopify.com" is legitimately tied to this body.
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle(data: WebhookMetadata.new(topic: "customers/update",
#      shop: "victim-shop.myshopify.com", body: {...attacker-controlled...}, ...))
```
The handler receives attacker-controlled data attributed to `victim-shop.myshopify.com`, even though the attacker never had any credential for that shop. [4](#0-3) [3](#0-2)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-43)
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

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
