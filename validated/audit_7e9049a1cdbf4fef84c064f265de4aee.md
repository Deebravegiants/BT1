## Title
Webhook `shop` (and `topic`) identity fields are trusted from unauthenticated headers while only the raw body is HMAC-verified, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by verifying an HMAC over the raw request body, then unconditionally trusts the `shop` (and `topic`) values taken from HTTP headers that are never included in the signed material. This breaks the identity binding `HMAC(payload) == HMAC(payload)` while the tenant-identifying `shop` claim is never cryptographically bound to that signature, allowing a legitimately-signed webhook (obtained by an attacker for their own shop) to be replayed against a victim shop's identity.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `api_version`, and `webhook_id` accessors are all read straight from HTTP headers with no cryptographic relationship to the HMAC: [2](#0-1) 

`HmacValidator.validate` only checks that `verifiable_query.to_signable_string` (i.e., the raw body) matches the received HMAC using the app's `api_secret_key`; it never verifies the `shop` header is bound to that body: [3](#0-2) 

`Registry.process` performs the HMAC check and then immediately trusts `request.shop` (and `request.topic`) to build the `WebhookMetadata` passed to the app's handler, without any check that this shop value was the one Shopify actually signed for: [4](#0-3) 

Documentation confirms host applications are expected to use `data.shop` as the authoritative tenant identifier for the webhook (e.g., to select which shop's records to update): [5](#0-4) 

The broken identity binding, stated as an equality:
- Expected: `shop_claimed_in_header == shop_that_Shopify_actually_signed_the_body_for`
- Actual: only `HMAC_received == HMAC_computed_over_raw_body` is checked; `shop` (and `topic`) are unauthenticated header values copied straight through to the handler.

### Impact Explanation
Because the `shop` header is never bound to the signed payload, an attacker who installs the app on their own (attacker-controlled) shop will receive genuinely Shopify-signed webhook deliveries (valid HMAC over the body) for that shop. Since HMAC validation is independent of the `x-shopify-shop-domain` header, the attacker can replay that same signed body to the app's webhook endpoint while substituting a victim shop's domain in the `shop-domain` header. `Utils::HmacValidator.validate` still succeeds (it only checks the body), and `Registry.process` passes `shop: <victim-shop>` to the handler. Any host application logic that uses `data.shop` to select which tenant's data to update (the documented, expected usage) will attribute attacker-controlled webhook content to the victim shop — a cross-tenant data/state confusion. This meets the "Critical - cross-tenant access" bar defined in scope.

### Likelihood Explanation
Reachable by any unprivileged internet user: they only need to install the target app on a shop they control (a normal, unprivileged install flow) to obtain a genuinely-signed webhook body/HMAC pair, then replay that request with a modified `shop-domain` header to the app's public webhook endpoint. No access token, `client_secret`, or privileged account is required — only the gem's own webhook-processing logic (`Registry.process`, `Request`, `HmacValidator`) is involved.

### Recommendation
Bind the tenant/topic identity to the signed material instead of trusting bare headers:
- Include `shop`, `topic`, `api_version`, and `webhook_id` in the HMAC-signed string (or otherwise verify them against Shopify's registered value for the delivering shop) before constructing `WebhookMetadata`.
- At minimum, document/enforce that the `shop` value from `Request#shop` must be cross-checked against a known/expected shop for the given endpoint or subscription before being used as a tenant identifier by host applications, and consider deriving `shop` from the verified body payload rather than from an unauthenticated header.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, receives a legitimate webhook delivery (e.g., `orders/create`) from Shopify with a valid `x-shopify-hmac-sha256` computed over the raw body using the app's real `api_secret_key`.
2. Attacker captures the raw body + HMAC value.
3. Attacker sends a POST to the app's webhook endpoint with the same raw body and HMAC, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers/body normally.
5. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only validates `raw_body` against the HMAC — the `shop` header is irrelevant to the check.
6. `handler.handle` is invoked with `data.shop == "victim-shop.myshopify.com"` even though the payload actually originated from, and was only ever signed for, `attacker-shop.myshopify.com`, causing any tenant-scoped processing in the host app to act on the wrong shop's context.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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

**File:** docs/usage/webhooks.md (L10-27)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```
